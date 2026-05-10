from pydantic import Field  
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.resource("docs://documents")
def list_documents():

    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}")
def get_document(doc_id: str):

    return docs.get(
        doc_id,
        "Document not found."
    )

# TODO: Write a tool to read a doc
@mcp.tool(
    name="read_doc_content",
    description="read the content of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    return docs[doc_id]
# TODO: Write a tool to edit a doc
@mcp.tool(
    name="edit doc_document",
    description="edit the content of a document. If the document does not exist, create it"
)
def edit_document(
    doc_id: str= Field(description="id of the document that will be edited"),
    old_str: str= Field(description="The text to replace. Must match exactky , including whitespace."),
    new_str: str= Field(description="the new text to insert  in place of the old text")
):
    if doc_id not in docs:
        raise ValueError(f"Doc id with { doc_id } not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
# TODO: Write a resource to return all doc id's
@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())
# TODO: Write a resource to return the contents of a particular doc
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs: 
        raise ValueError(f"Doc id with { doc_id } not found")
    return docs[doc_id]
# TODO: Write a prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="rewrites the contents of the document in markdown format"
)
def format_document(
    doc_id: str= Field(description="id of the document to format")
) -> list[base.Message]:
    prompt = """
        your goal is to reformat a document to be writeen with markdwon syntax.

        The id of the document to you need to reformat is:
        <document_id>
        {doc_id}
        <document_id>

        add in headers, bullet points, tables, etc as necessary to make the document well-formatted markdown. 
      """
    
    return [base.UserMessage(prompt)]
# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
