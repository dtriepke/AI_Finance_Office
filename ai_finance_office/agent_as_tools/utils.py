# Deep Lake Vector Store
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.deeplake import DeepLakeVectorStore
from llama_index.core import VectorStoreIndex, ServiceContext

import os 

os.environ['ACTIVELOOP_TOKEN'] = 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpZCI6ImRlbm5pc3RyaWVwa2UiLCJhcGlfa2V5IjoiRmZfRlMwZGh4S0dNcERSb0xueDJ0X25kcEtoRXM1MDhtcHdWRlFBdFZCc1hfIn0.'
# service_context = ServiceContext.from_defaults(llm=llm_gpt4)

def create_index_from_db_with_DeepLakeVectorStore(org_id, dataset_name, overwrite=False):
    """
    Create an index from database.

    Parameters:
    org_id (str): Organization ID for Activeloop.
    dataset_name (str): Name of the dataset for Activeloop.

    Returns:
    VectorStoreIndex: The created index.
    """

    # Set up the dataset path
    dataset_path = f"hub://{org_id}/{dataset_name}"

    # Create an index over the documents
    vector_store = DeepLakeVectorStore(dataset_path=dataset_path, overwrite=overwrite)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    document_index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    return document_index

# For initiating
def create_index_from_file_with_DeepLakeVectorStore(documents, org_id, dataset_name, overwrite=True):
    """
    Create an index from a given file.

    Parameters:
    document (list): llamaindex Documents object.
    org_id (str): Organization ID for Activeloop.
    dataset_name (str): Name of the dataset for Activeloop.

    Returns:
    VectorStoreIndex: The created index.
    """

    # Set up the dataset path
    dataset_path = f"hub://{org_id}/{dataset_name}"

    # Create an index over the documents
    vector_store = DeepLakeVectorStore(dataset_path=dataset_path, overwrite=overwrite)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    document_index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    return document_index
