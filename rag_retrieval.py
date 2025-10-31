"""
RAG (Retrieval Augmented Generation) functions for report generation
"""

from vector_db import query_vectordb, initialize_chromadb

# This function searches your vector database (ChromaDB) to find the most relevant pieces of information (documents or records) related to the user’s query
# For example -> Show top performing marketing campaigns in Q3.
# filter_type: you can choose to limit the search to "sales" or "marketing" data.
def retrieve_relevant_context(query, n_results=5, filter_type=None):
    """Retrieve relevant context from vector database based on query"""
    _,collection = initialize_chromadb() # This connects to vector database (ChromaDB).

    # If you passed filter_type="sales", then filter_dict becomes {"type": "sales"}.
    # This tells the database: Only give me documents where type = sales.
    # If no filter is given → filter_dict stays None, and it searches everything.
    filter_dict = None
    if filter_type:
        filter_dict = {'type': filter_type}
    
    # It returns the most similar documents
    # Each result includes:
        #1. documents: the matching text chunks
        #2. metadatas: details like region, revenue, campaign name, etc.
        #3. distances: how close each document is to your query (lower = better)
    results = query_vectordb(collection, query, n_results=n_results, filter_dict=filter_dict)

    return results
    """
    {
  'documents': [["Campaign A data", "Campaign B data", "Campaign C data"]],
  'metadatas': [[{'type': 'marketing', 'channel': 'Facebook'}, {...}, {...}]],
  'distances': [[0.12, 0.25, 0.37]]
    }

    """
def format_retrieval_results(results):
    """Format retrieval results into readable context"""
    if not results or not results.get("documents"):
        return "No relevant information found."
    
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    formatted_context = []

    # enumerate() gives both index (i) and the actual data (doc, metadata, distance)
    for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        context_item = {
            "rank": i+1, # The position of this result (1st, 2nd, 3rd, etc.)
            "relevance_score": 1 - distance, # Converts distance into a more intuitive similarity score (since 1 - distance means: smaller distance = higher similarity)
            "type": metadata.get("type", "unknown"), # Pulls the “type” field from metadata (sales, marketing, etc.)
            "content": doc, # The actual retrieved document text
            "metadata": metadata # Keeps all metadata info for further use
        }

        formatted_context.append(context_item)
    return formatted_context
    """
    [
  {
    "rank": 1,
    "relevance_score": 0.91,
    "type": "sales",
    "content": "Q3 Sales revenue increased by 12%",
    "metadata": {"type": "sales", "region": "Europe"}
  },
  {
    "rank": 2,
    "relevance_score": 0.73,
    "type": "marketing",
    "content": "Campaign B generated 25% more leads",
    "metadata": {"type": "marketing", "channel": "Facebook"}
  }
    ]
    """
# Takes the structured list returned by format_retrieval_results() and turns it into a clean text summary that can be directly passed into the LLM prompt
def create_context_string(formatted_context):
    # If the previous step returned a string (no data found), it just passes that text along — no need to format it further.
    if isinstance(formatted_context, str):
        return formatted_context
    
    # Initializes a list that will hold text lines.
    context_parts = ["Retrieved relevant information:\n"]

    for item in formatted_context:
        # 1. [SALES] (Relevance: 0.91)
        context_parts.append(f"\n{item['rank']}. [{item['type'].upper()}] (Relevance: {item['relevance_score']:.2f})")
        #   Q3 Sales revenue increased by 12%
        context_parts.append(f"   {item['content']}")
        
        # Add key metadata
        metadata = item['metadata']
        if item["type"] == "sales":
            # If it’s a sales record, it adds info like Product, Revenue, Region, Quarter.
            context_parts.append(f"   Product: {metadata.get('product')}, Revenue: ${metadata.get('revenue')}, Region: {metadata.get('region')}, Quarter: {metadata.get('quarter')}")
        elif item["type"] == "marketing":
            # If it’s a marketing record, it adds Campaign, Channel, Budget, Conversions.
            context_parts.append(f"   Campaign: {metadata.get('campaign_name')}, Channel: {metadata.get('channel')}, Budget: ${metadata.get('budget')}, Conversions: {metadata.get('conversions')}")
    
    # Joins all lines with newline characters.
    return "\n".join(context_parts)

    """
    Retrieved relevant information:

    1. [SALES] (Relevance: 0.91)
    Q3 sales revenue increased by 12%.
    Product: Widget A, Revenue: $500000, Region: North America, Quarter: Q3

    2. [MARKETING] (Relevance: 0.82)
    Email campaign generated strong engagement.
    Campaign: Spring Blast, Channel: Email, Budget: $10000, Conversions: 230

    """
# A specialized helper that retrieves and formats sales-related information from your vector database.
# here we pass filter_type="sales" — so it only searches for documents tagged with type = "sales" in vector store (like ChromaDB).
def retrieve_sales_data(query, n_results=5):
    # Retrieve from the vector database
    results = retrieve_relevant_context(query, n_results=n_results, filter_type="sales")
    # This converts raw ChromaDB output into a cleaner list of dictionaries
    formatted = format_retrieval_results(results)
    # This turns your formatted results into a natural-language summary. That text is perfect for passing into an LLM prompt.
    return create_context_string(formatted)

def retrieve_marketing_data(query, n_results=5):
    """Retrieve marketing-specific data"""
    results = retrieve_relevant_context(query, n_results=n_results, filter_type="marketing")
    formatted = format_retrieval_results(results)
    return create_context_string(formatted)

def retrieve_combined_data(query, n_results=5):
    """Retrieve both sales and marketing data"""
    results = retrieve_relevant_context(query, n_results=n_results)
    formatted = format_retrieval_results(results)
    return create_context_string(formatted)

if __name__ == "__main__":
    # Test RAG retrieval
    print("Testing RAG retrieval...")
    query = "What are the top performing products in North America?"
    context = retrieve_combined_data(query, n_results=3)
    print(f"\nQuery: {query}")
    print(f"\nContext:\n{context}")










