TARGET      := bin/privipchanger
CORE_DIR    := core
INC_DIR     := include
BUILD_DIR   := build
BIN_DIR     := bin

CC          := gcc
CFLAGS      := -Wall -Wextra -O3 -I$(INC_DIR) -MMD
LDFLAGS     := -lpcap

SRCS        := $(wildcard $(CORE_DIR)/*.c)
OBJS        := $(patsubst $(CORE_DIR)/%.c, $(BUILD_DIR)/%.o, $(SRCS))
DEPS        := $(OBJS:.o=.d)


all: $(TARGET)

$(TARGET): $(OBJS)
	@mkdir -p $(BIN_DIR)
	@$(CC) $(OBJS) -o $@ $(LDFLAGS)
	@echo "PROJECT COMPILED: $@"

$(BUILD_DIR)/%.o: $(CORE_DIR)/%.c
	@mkdir -p $(BUILD_DIR)
	@$(CC) $(CFLAGS) -c $< -o $@
	@echo "Compiled: $<"

-include $(DEPS)


clean:
	@rm -rf $(BUILD_DIR) $(BIN_DIR)/privipchanger
	@echo "CLEAN COMPLETED (build/ and bin/privipchanger removed)"

help:
	@echo "Available commands:"
	@echo "  make       - Builds the privipchanger binary"
	@echo "  make clean - Removes temporary files and the binary"
	@echo "  make help  - Shows this help message"

.PHONY: all clean help

