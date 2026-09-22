from typing import BinaryIO


class BlobStorage:
    def __init__(self, connection_string: str | None, container: str):
        self._client = None
        if connection_string:
            from azure.storage.blob import BlobServiceClient

            service = BlobServiceClient.from_connection_string(connection_string)
            self._client = service.get_container_client(container)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def upload(self, blob_name: str, content: BinaryIO, content_type: str | None = None) -> str:
        if not self._client:
            raise RuntimeError("Blob storage is not configured")
        from azure.storage.blob import ContentSettings

        self._client.upload_blob(
            name=blob_name,
            data=content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type)
            if content_type
            else None,
        )
        return blob_name
