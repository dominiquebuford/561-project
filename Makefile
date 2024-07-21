#define variables
DOCKER_NAME = photos-app-backend
SOURCE_DIR = backend
TEST_DIR = backend

#define commands
LINTER = flake8
TESTER = pytest

.PHONY: install lint test build all

#install my dependencies
install:
	pip install -r $(SOURCE_DIR)/requirements.txt

#Lint code in backend folder
lint:
	$(LINTER) $(SOURCE_DIR)

test:
	$(TESTER) $(TEST_DIR)

build:
	docker build -t $(DOCKER_NAME) $(SOURCE_DIR)

all: install lint test build
	@echo


