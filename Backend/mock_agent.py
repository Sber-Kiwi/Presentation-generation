import sys
import json
import time

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            task_id = req.get("task_id")
            action = req.get("action")
            
            # Simple heuristic: if prompt/edit_prompt/slides are missing, it's a ping
            if "prompt" not in req and "edit_prompt" not in req and "slides" not in req:
                print(json.dumps({"task_id": task_id, "status": "ready"}), flush=True)
            else:
                # It's the full payload
                print(json.dumps({"task_id": task_id, "status": "accepted"}), flush=True)
                
                # Mock a small delay to simulate processing
                time.sleep(2)
                
                if action == "generate":
                    # return a list of 2 mock slides
                    mock_slides = [
                        {"title": "Mock Slide 1", "content": "This is generated content"},
                        {"title": "Mock Slide 2", "content": "More mock content"}
                    ]
                    print(json.dumps({"task_id": task_id, "result": mock_slides}), flush=True)
                elif action == "edit":
                    # return a single mock edited slide
                    mock_edited_slide = {"title": "Edited Slide", "content": "This is edited content"}
                    print(json.dumps({"task_id": task_id, "result": mock_edited_slide}), flush=True)
                elif action == "export":
                    # return a string representing the final JSON
                    mock_final = json.dumps({
                        "meta": {"common_slide_title": "Mock Presentation", "title": "Mock Title"},
                        "slides": [
                            {
                                "meta": {"title": "Exported Slide"},
                                "objects": []
                            }
                        ]
                    })
                    print(json.dumps({"task_id": task_id, "result": mock_final}), flush=True)
                    
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}), flush=True)

if __name__ == "__main__":
    main()
