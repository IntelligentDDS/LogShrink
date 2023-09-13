cc = g++
EXEC = THULR
SRCS = main.cpp template.cpp LengthSearch.cpp
OBJS = $(SRCS:.cpp=.o)

start:$(OBJS)
	$(cc) -o $(EXEC) $(OBJS)
	$(cc) -std=c++11 elastic.cpp -o Elastic

.cpp.o:
	$(cc) -std=c++11 -o $@ -c $<
clean:
	rm -rf $(OBJS) $(EXEC)
	rm -rf Elastic 

