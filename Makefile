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


# V=1 shows the compiler invocations, and therefore the warnings
V           ?= 0
ifeq ($(V),1)
Q           :=
else
Q           := @
endif

CAPS        := cap_net_raw,cap_net_admin+ep

all: $(TARGET) setcap

$(TARGET): $(OBJS)
	$(Q)mkdir -p $(BIN_DIR)
	$(Q)$(CC) $(OBJS) -o $@ $(LDFLAGS)
	@echo "PROJECT COMPILED: $@"

$(BUILD_DIR)/%.o: $(CORE_DIR)/%.c
	$(Q)mkdir -p $(BUILD_DIR)
	$(Q)$(CC) $(CFLAGS) -c $< -o $@
	@echo "Compiled: $<"

# Capabilities live on the inode, so every relink throws them away
setcap: $(TARGET)
	@if sudo -n setcap '$(CAPS)' $(TARGET) 2>/dev/null; then \
	  echo "Capabilities set: $(CAPS)"; \
	else \
	  echo "NOTE: run 'sudo setcap $(CAPS) $(TARGET)' - the binary needs it to run unprivileged"; \
	fi

-include $(DEPS)


clean:
	@rm -rf $(BUILD_DIR) $(BIN_DIR)/privipchanger
	@echo "CLEAN COMPLETED (build/ and bin/privipchanger removed)"

help:
	@echo "Available commands:"
	@echo "  make        - Builds the privipchanger binary and applies capabilities"
	@echo "  make V=1     - Same, but shows the compiler invocations and warnings"
	@echo "  make setcap  - Re-applies cap_net_raw,cap_net_admin to the binary"
	@echo "  make clean   - Removes temporary files and the binary"
	@echo "  make help    - Shows this help message"

.PHONY: all clean help setcap

