# AlgoBot

*AlgoBot* is a crude algorithmic trading system. 
The idea, currently, is to focus primarily on trading equities via what can be considered daily, weekly, or monthly 
rebalances.
The strategies will be diverse and most likely horrible. Benchmark
indexes will be chosen based on the modal sector
across all portfolio allocations.

The backend scripts will leverage numpy/pandas for computations, and serve
data on these auto-traded 'portfolios' (via  a Flask API) to a React/TS frontend, acting as a dashboard of sorts.

### TODO
- [x] Set up basic entity/class definitions
- [x] Establish database functionality
- [x] Write methods to ensure data is up-to-date, and refresh if needed
- [ ] Write methods to calculate technical indicators
- [ ] Write methods to help with fundamental analysis
- [ ] Research, design, and implement trading strategies
- [ ] **UNIT TESTS** probably useful at some point 
- [ ] Set up Flask API
- [ ] Develop barebones React frontend
- [ ] Hook frontend to API
