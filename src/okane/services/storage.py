"""Storage backend abstraction for local and cloud storage."""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def write_file(self, content: bytes, destination_path: str) -> None:
        """Write file content to storage.

        Args:
            content: File content as bytes
            destination_path: Relative path where file should be stored

        Raises:
            IOError: If write operation fails
        """
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> bytes:
        """Read file content from storage.

        Args:
            file_path: Relative path to file

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If read operation fails
        """
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Check if file exists in storage.

        Args:
            file_path: Relative path to file

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def get_full_path(self, relative_path: str) -> str:
        """Get full path for a relative path.

        Args:
            relative_path: Relative path within storage

        Returns:
            Full path string
        """
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend with atomic writes."""

    def __init__(self, base_path: str | Path) -> None:
        """Initialize local storage backend.

        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_file(self, content: bytes, destination_path: str) -> None:
        """Write file content to local filesystem atomically.

        Uses temporary file + rename for atomic write operation.

        Args:
            content: File content as bytes
            destination_path: Relative path where file should be stored

        Raises:
            IOError: If write operation fails
        """
        full_path = self.base_path / destination_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first, then rename (atomic operation)
        fd, temp_path = tempfile.mkstemp(dir=full_path.parent, prefix=".tmp_")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(content)
            # Atomic rename
            os.replace(temp_path, full_path)
        except Exception:
            # Clean up temp file if something goes wrong
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise

    def read_file(self, file_path: str) -> bytes:
        """Read file content from local filesystem.

        Args:
            file_path: Relative path to file

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If read operation fails
        """
        full_path = self.base_path / file_path
        with open(full_path, "rb") as f:
            return f.read()

    def exists(self, file_path: str) -> bool:
        """Check if file exists in local filesystem.

        Args:
            file_path: Relative path to file

        Returns:
            True if file exists, False otherwise
        """
        full_path = self.base_path / file_path
        return full_path.exists()

    def get_full_path(self, relative_path: str) -> str:
        """Get full local filesystem path.

        Args:
            relative_path: Relative path within storage

        Returns:
            Full filesystem path as string
        """
        return str(self.base_path / relative_path)


class ADLSStorageBackend(StorageBackend):
    """Azure Data Lake Storage Gen2 backend."""

    def __init__(
        self,
        account_name: str,
        account_key: str,
        filesystem_name: str,
        base_path: str = "",
    ) -> None:
        """Initialize ADLS Gen2 storage backend.

        Args:
            account_name: Azure storage account name
            account_key: Azure storage account key
            filesystem_name: ADLS Gen2 filesystem (container) name
            base_path: Base path within filesystem (default: root)

        Raises:
            ImportError: If azure-storage-file-datalake is not installed
            ValueError: If credentials are invalid
        """
        try:
            from azure.storage.filedatalake import DataLakeServiceClient
        except ImportError as e:
            raise ImportError(
                "azure-storage-file-datalake is required for ADLS Gen2 support. "
                "Install with: uv add azure-storage-file-datalake"
            ) from e

        self.account_name = account_name
        self.filesystem_name = filesystem_name
        self.base_path = base_path.strip("/")

        # Create service client
        account_url = f"https://{account_name}.dfs.core.windows.net"
        self.service_client = DataLakeServiceClient(account_url=account_url, credential=account_key)

        # Get filesystem client
        self.filesystem_client = self.service_client.get_file_system_client(filesystem_name)

    def write_file(self, content: bytes, destination_path: str) -> None:
        """Write file content to ADLS Gen2.

        Args:
            content: File content as bytes
            destination_path: Relative path where file should be stored

        Raises:
            IOError: If write operation fails
        """
        full_path = f"{self.base_path}/{destination_path}".strip("/")
        file_client = self.filesystem_client.get_file_client(full_path)

        try:
            file_client.upload_data(content, overwrite=True)
        except Exception as e:
            raise OSError(f"Failed to write to ADLS Gen2: {e}") from e

    def read_file(self, file_path: str) -> bytes:
        """Read file content from ADLS Gen2.

        Args:
            file_path: Relative path to file

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If read operation fails
        """
        full_path = f"{self.base_path}/{file_path}".strip("/")
        file_client = self.filesystem_client.get_file_client(full_path)

        try:
            download = file_client.download_file()
            return download.readall()
        except Exception as e:
            if "PathNotFound" in str(e):
                raise FileNotFoundError(f"File not found: {file_path}") from e
            raise OSError(f"Failed to read from ADLS Gen2: {e}") from e

    def exists(self, file_path: str) -> bool:
        """Check if file exists in ADLS Gen2.

        Args:
            file_path: Relative path to file

        Returns:
            True if file exists, False otherwise
        """
        full_path = f"{self.base_path}/{file_path}".strip("/")
        file_client = self.filesystem_client.get_file_client(full_path)

        try:
            file_client.get_file_properties()
            return True
        except Exception:
            return False

    def get_full_path(self, relative_path: str) -> str:
        """Get full ADLS Gen2 path.

        Args:
            relative_path: Relative path within storage

        Returns:
            Full ADLS path in abfss:// format
        """
        full_path = f"{self.base_path}/{relative_path}".strip("/")
        return (
            f"abfss://{self.filesystem_name}@{self.account_name}.dfs.core.windows.net/{full_path}"
        )
