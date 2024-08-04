# invest
Trying out DeepMind reinforcement learning / neural net concepts

Tic Tac Toe is basic but working.

This will be a try at an investment game.

Players are different:
    Player 1 is me, the investor, deciding to buy and sell.
    Player 2 is Mr. Market, deciding how to alter prices.

So there will be no winner or loser, only my final score at the end of the game, which I seek to maximize.

Turns will go one per day.  Each day:

    I'll have company information from financials
    I'll have a price at which I can trade
    My turn will consist of a decision to buy, sell, or do nothing.
        Start with a cash stake, say USD 10,000.
        If I buy, it will be with all the cash I have
        If I don't buy, the amount remains in cash (maybe earn cash return later)
        If I sell, I sell everything, converting back to cash

    I make my move, the Mr. Market makes his move
        Mr. Market adjusts the market price for the asset.

    My learning will consist of assessing relative value of the asset, based on company fundamentals, and on market price.
    At outset, I'll have no historic price knowledge, only company financials.
    I'll need to seed with baseline values at start: e.g., P/E of 10 or less is buyable, etc.