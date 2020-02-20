.PHONY: format help

# Help system from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


up: ## Run all the containers in the background
	docker-compose up -d --build

ps: ## Show currently running containers
	docker-compose ps

logs: ## Begin streaming logs to terminal
	docker-compose logs -f

stop: ## Stop all containers
	docker-compose stop

start: ## Start all containers
	docker-compose start

down: ## Stop and remove all containers
	docker-compose down --remove-orphans

clean: ## Stop and remove all containers and their data
	rm -rf ./data/*

useradd: ## Create IAM user for performing log syncing
	aws iam create-user --user-name logs || echo "[+] User exists"
	aws iam attach-user-policy --user-name logs --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess || echo "[+] Policy is attached"
	aws iam attach-user-policy --user-name logs --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess || echo "[+] Policy is attached"
	aws iam create-access-key --user-name logs || echo "[+] Access keys exist"

userdel: ## Delete IAM user for log syncing
	aws iam detach-user-policy --user-name logs --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess || echo "[+] Policy is detached"
	aws iam detach-user-policy --user-name logs --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess || echo "[+] Policy is detached"
	aws iam list-access-keys --user-name logs | jq -r '.AccessKeyMetadata[] | .AccessKeyId' | xargs -I{} aws iam delete-access-key --access-key-id {} --user-name logs || echo "[+] Access keys deleted"
	aws iam delete-user --user-name logs || echo "[+] User deleted"

configure: ## Create a .env file
	python ./configure.py
