.PHONY: local modal-deploy

local:
	cd src && uvicorn main:fastapi_app --reload --host 0.0.0.0 --port 8000

deploy:
	cd src && modal deploy modal_deploy.py 