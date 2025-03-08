from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "shibing624/text2vec-base-chinese",
    backend="onnx",
    model_kwargs={"file_name": "model_qint8_avx512_vnni.onnx"},
)
embeddings = model.encode(["結構性混泥土", "泥土", "鋼筋"])
print(embeddings.shape)
similarities = model.similarity(embeddings, embeddings)
print(similarities)
