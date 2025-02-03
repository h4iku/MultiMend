import textwrap
import uuid

import chromadb
from more_itertools import batched
from sentence_transformers import SentenceTransformer

from .configs import chromadb_path


class RAG:
    def __init__(self, collection_name):
        model_args = {
            "model_name_or_path": "all-MiniLM-L6-v2",
            "trust_remote_code": True,
        }

        self.model = SentenceTransformer(**model_args)

        self.client = chromadb.PersistentClient(path=str(chromadb_path))
        self.collection_name = collection_name

    def create_collection(self) -> None:
        """Drop if exists and create a new collection based on `self.collection_name`"""

        self.client.get_or_create_collection(self.collection_name)
        self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            self.collection_name,
            metadata={"hnsw:space": "cosine", "hnsw:M": 1024},
        )

    def split(self, code: str) -> list[str]:
        """Split given code into chunks"""

        return [" ".join(line.split()) for line in code.splitlines()]

    def embed(
        self, data: list[str], metadatas: list[dict], save_docs: bool = True
    ) -> None:
        """Embed and store chunks into a vectore store"""

        collection = self.client.get_collection(self.collection_name)
        embeddings = self.model.encode(data, batch_size=32)

        for batch in batched(
            zip(embeddings.tolist(), data, metadatas),
            self.client.get_max_batch_size(),
        ):
            batched_embeddings, batched_documents, batched_metadatas = zip(*batch)
            collection.add(
                ids=[str(uuid.uuid4()) for _ in range(len(batch))],
                embeddings=list(batched_embeddings),
                metadatas=list(batched_metadatas),
                documents=list(batched_documents) if save_docs else None,
            )

    def retrieve(
        self, query: str, query_metadata: dict, n_return: int, threshold: float = None
    ) -> tuple[list[str], list[str]]:
        """Retrieve top-n chunks based on the given query"""

        embeddings = self.model.encode(query, batch_size=32)

        collection = self.client.get_collection(self.collection_name)
        results = collection.query(
            query_embeddings=embeddings.tolist(),
            n_results=n_return,
            where=(
                {"$and": [{k: v} for k, v in query_metadata.items()]}
                if len(query_metadata) > 1
                else query_metadata
            ),
        )

        if threshold:
            filtered = [d for d in results["distances"][0] if d <= threshold]
            return results["documents"][0][: len(filtered)], results["metadatas"][0][
                : len(filtered)
            ]
        else:
            return results["documents"][0], results["metadatas"][0]


def main():
    from pprint import pprint

    code = textwrap.dedent(
        """\
        public class FIND_IN_SORTED {
            public static int binsearch(int[] arr, int x, int start, int end) {
                if (start == end) {
                    return -1;
                }
                int mid = start + (end - start) / 2; // check this is floor division
                if (x < arr[mid]) {
                    return binsearch(arr, x, start, mid);
                } else if (x > arr[mid]) {
                    return binsearch(arr, x, mid, end);
                } else {
                    return mid;
                }
            }

            public static int find_in_sorted(int[] arr, int x) {
                return binsearch(arr, x, 0, arr.length);
            }
        }
    """
    )

    rag = RAG("test")
    rag.create_collection()
    split_code = rag.split(code)
    pprint(split_code)
    metadata = {"bugid": "qb", "hunk": 0}
    rag.embed(split_code, [metadata] * len(split_code))
    docs, metas = rag.retrieve("return binsearch(arr, x, mid, end);", metadata, 10)
    pprint(docs)
    print(len(" ".join(docs).split()))
    docs, metas = rag.retrieve("return binsearch(arr, x, mid, end);", metadata, 10, 0.3)
    pprint(docs)
    print(len(" ".join(docs).split()))


if __name__ == "__main__":
    main()
