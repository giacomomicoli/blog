.PHONY: start, stop
RED	:= \033[0;31m
GREEN	:= \033[0;32m
YELLOW	:= \033[0;33m
RESET	:= \033[0m

ENVIRONMENT ?= development
CONTAINER_TO_LOG ?= blog

start:
	@printf "${GREEN}Starting Docker containers in ${ENVIRONMENT} environment...${RESET}\n"
	docker-compose up -d

stop:
	@printf "${RED}Stopping Docker containers in ${ENVIRONMENT} environment...${RESET}\n"
	docker-compose down

reload:
	@printf "${YELLOW}Reloading Docker containers in ${ENVIRONMENT} environment...${RESET}\n"
	docker-compose down
	docker-compose up -d
logs:
	@printf "${YELLOW}Tailing logs for container: ${CONTAINER_TO_LOG}${RESET}\n"
	docker logs -f $(CONTAINER_TO_LOG)

stop-logs:
	@printf "${YELLOW}Stopping log tailing for container: ${CONTAINER_TO_LOG}${RESET}\n"
	@# This target is a placeholder; stopping logs is done by interrupting the logs command (Ctrl+C)
	@echo "To stop logging, please interrupt the logs command (Ctrl+C)."
