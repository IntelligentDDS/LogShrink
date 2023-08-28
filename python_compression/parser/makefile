cc = g++
EXEC = THULR
SRCS = main.cpp template.cpp LengthSearch.cpp
OBJS = $(SRCS:.cpp=.o)

start:$(OBJS)
	$(cc) -o $(EXEC) $(OBJS)

.cpp.o:
	$(cc) -std=c++11 -o $@ -c $<
clean:
	rm -rf $(OBJS) $(EXEC)