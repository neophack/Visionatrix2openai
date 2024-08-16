from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal
import time
import httpx
import json
import base64
import os

app = FastAPI()
router = APIRouter()

# 获取环境变量中的 BASE_URL
BASE_URL = os.getenv("IMAGE_GENERATION_BASE_URL", "http://172.16.134.251:8288")
MODEL = os.getenv("IMAGE_GENERATION_MODEL", "flux1_dev_8bit")

# 请求体模型
class ImageGenerationRequest(BaseModel):
    prompt: constr(max_length=4000)
    model: Optional[str] = "dall-e-2"
    n: Optional[int] = Field(1, ge=1, le=10)
    quality: Optional[Literal["standard", "hd"]] = "standard"
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]] = "1024x1024"
    style: Optional[Literal["vivid", "natural"]] = "vivid"
    user: Optional[str] = None

# 响应体模型
class ImageData(BaseModel):
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    created: int
    data: List[ImageData]

@router.post("/generations", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    # 检查模型是否支持
    if request.model not in ["dall-e-2", "dall-e-3"]:
        raise HTTPException(status_code=400, detail="Model not supported")

    # 检查生成的图像数量（特别是对于 dall-e-3）
    if request.model == "dall-e-3" and request.n != 1:
        raise HTTPException(status_code=400, detail="For dall-e-3, only n=1 is supported")

    # 调用创建任务的API
    create_task_url = f"{BASE_URL}/api/tasks/create"
    task_params = {
        "name": MODEL,
        "count": request.n,
        "input_params": json.dumps({
            "prompt": request.prompt,
            "in_param_27": "1:1 (1024x1024)",
            "realism_lora_strength": 0,
        }),
    }

    async with httpx.AsyncClient() as client:
        create_response = await client.post(create_task_url, data=task_params)
        if create_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to create task")
        task_data = create_response.json()
        task_ids = task_data.get("tasks_ids", [])

    # 检查任务进度并获取结果
    generated_images = []
    for task_id in task_ids:
        progress_url = f"{BASE_URL}/api/tasks/progress/{task_id}"
        for i in range(100):
            async with httpx.AsyncClient() as client:
                progress_response = await client.get(progress_url)
                progress_data = progress_response.json()
                if progress_data["progress"] == 100.0:
                    node_id = progress_data["outputs"][0]["comfy_node_id"]
                    break
                time.sleep(1)  # 等待一秒钟再检查进度
            if i == 99:
                return ImageGenerationResponse(
                    created=int(time.time()),
                    data=generated_images
                )

        # 获取生成的图像
        result_url = f"{BASE_URL}/api/tasks/results?task_id={task_id}&node_id={node_id}"
        async with httpx.AsyncClient() as client:
            result_response = await client.get(result_url)

            if result_response.status_code == 200:
                if request.response_format == "url":
                    generated_images.append(ImageData(
                        url=result_url,
                        revised_prompt=request.prompt  # 这里假设 revised_prompt 等于原始 prompt
                    ))
                elif request.response_format == "b64_json":
                    b64_json = "data:image/png;base64," + base64.b64encode(result_response.content).decode('utf-8')
                    generated_images.append(ImageData(
                        b64_json=b64_json,
                        revised_prompt=request.prompt  # 这里假设 revised_prompt 等于原始 prompt
                    ))

    response = ImageGenerationResponse(
        created=int(time.time()),
        data=generated_images
    )

    return response

app.include_router(router, prefix="/v1/images")
