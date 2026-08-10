for i in $(seq 1 5); do
    curl -s -X POST http://localhost:8000/ask \
        -H "Content-Type: application/json" \
        -H. "X-API-Key: $AGENT_API_KEY" \
        -d. '{"question": "Xin chào lần '"$i"'"}' | python3 -m json.tool
    echo. "---"