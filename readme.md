##
FLUX to DALL-E 3 server

###
[https://github.com/Visionatrix/Visionatrix](https://github.com/Visionatrix/Visionatrix)

### docker
```shell
docker build -t vx2openai .
docker run -p 8000:8000 -e IMAGE_GENERATION_BASE_URL=http://172.16.134.251:8288 -e IMAGE_GENERATION_MODEL=flux1_dev_8bit_neo vx2openai  
```
### test
```shell
curl -X POST "http://127.0.0.1:8000/cation/json" -d '{s"   -H "Content-Type: applic
    "model": "dall-e-3",
    "prompt": "A cute baby sea otter",
    "n": 1,
    "size": "1024x1024"
  }'
```
```json
{"created":1723801829,"data":[{"url":"http://172.16.134.251:8288/api/tasks/results?task_id=64&node_id=9","b64_json":null,"revised_prompt":"A cute baby sea otter"}]}
```
