# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -std=c++11

# Source directories (you can add more directories if needed)
SRC_DIRS := Communication DeviceDrivers

# Object directory
OBJ_DIR := objects

# Find all .cpp and .h files in the source directories
SRCS := $(shell find $(SRC_DIRS) -name '*.cpp')
OBJS := $(SRCS:.cpp=.o)

# Executable name
TARGET = my_program

# Default target to build the executable
all: $(OBJ_DIR) $(TARGET)

# Create object directory if it doesn't exist
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Link object files to create the executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(addprefix $(OBJ_DIR)/, $(notdir $(OBJS)))

# Compile .cpp files into .o object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@
	@mv $@ $(OBJ_DIR)

# Clean up object files and executable
clean:
	rm -f $(OBJ_DIR)/*.o $(TARGET)

# Indicate that the headers are dependencies
$(OBJS): $(shell find $(SRC_DIRS) -name '*.h')
