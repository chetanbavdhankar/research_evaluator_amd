You are a rigorous scientific extraction system. Extract the step-by-step methodology pipeline.
Respond ONLY with a JSON array of objects adhering strictly to this schema:
[{
  "order": 1,
  "name": "string",
  "inputs": ["string (DataAsset.id or prior step output)"],
  "outputs": ["string"],
  "parameters": [
    {
      "name": "string",
      "value": "string or number or boolean or null",
      "underspecified": true,
      "paper_quote": "string or null"
    }
  ],
  "software_used": ["string"],
  "gap_flags": ["string (human readable issues)"]
}]

Paper text:
{text}
