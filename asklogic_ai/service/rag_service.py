from asklogic_ai.service.retriever import retrieve_documents
from asklogic_ai.service.generator import generate_answer
from asklogic_ai.model.schemas import AskResponse

class RAGService:
    async def answer_question(self, question: str) -> AskResponse:
        # Step 1: Retrieve relevant documents
        docs = retrieve_documents(question)

        # Step 2: Create prompt
        context = "\n\n".join(docs)
        prompt = f"""Answer the following question based on the context below. 
If the context is not relevant, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

        # Step 3: Generate answer
        answer = await generate_answer(prompt)

        return AskResponse(
            question=question,
            answer=answer,
            retrieved=docs
        )
