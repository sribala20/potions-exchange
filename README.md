# Central Coast Cauldrons

Central Coast Cauldrons is a stubbed out API that integrates with a persistance layer. The backend interacts with the [Potion Exchange](https://potion-exchange.vercel.app/), where simulated customers will shop at the store using the API. 

The application's setting is a simulated fantasy RPG world with adventurers seeking to buy potions.

# Building the application
* Integrates with Render for hosting and Supabase for database management
* Implemented real-time inventory tracking and order management systems, ensuring accurate stock levels and preventing overselling
* Designed and built a flexible, database-driven system for custom product creation, allowing for dynamic expansion of product offerings
* Created a ledger-based inventory system, enabling detailed transaction history tracking and facilitating auditing processes
* Created a search functionality with filtering, pagination, and sorting capabilities

## Understanding the Game Mechanics

With an initial capital of 100 gold, no potions in your inventory, and devoid of barrels, your backend API is scheduled to be invoked at regular intervals, known as 'ticks' that go off every two hours. There are 12 ticks in a day, and 7 days in a week. The weekdays in the Potion Exchange world are:
1. Edgeday
1. Bloomday
1. Aracanaday
1. Hearthday
1. Crownday
1. Blesseday
1. Soulday

There are three primary actions that may unfold during these ticks:

1. **Customer Interactions**: On each tick, one or more simulated customers access your catalog endpoint intending to buy potions. The frequency and timing of customer visits vary based on the time of day, and each customer exhibits specific potion preferences. Your shop's performance is evaluated and scored based on multiple criteria (more details on [Potion Exchange](https://potion-exchange.vercel.app/)), which in turn influences the frequency of customer visits.

2. **Potion Creation**: Every alternate tick presents an opportunity to brew new potions. Each potion requires 100 ml of any combination of red, green, blue, or dark liquid. You must have sufficient volume of the chosen color in your barrelled inventory to brew a potion.

3. **Barrel Purchasing**: On every alternate tick, you have an opportunity to purchase additional barrels of various colors. Your API receives a catalog of barrels available for sale and should respond with your purchase decisions. The gold cost of each barrel is deducted from your balance upon purchase.

Part of the challenge in these interactions is you are responsible for keeping track of your gold and your various inventory levels. The [Potion Exchange](https://potion-exchange.vercel.app/) separately keeps an authoritiative record (which can be viewed under Shop stats).

### Customers
Customers of various types have different seasonality on when they show up. For example, some customers are more likely to shop on certain days of the week and at certain times of day. Customers each have their own class which has a huge impact on what types of potions that customer is looking for. The amount a customer is willing to spend on a given potion depends on both the customers own level of wealth and how precisely the potions available in a store match their own preference.

Lastly, customers are more likely to shop in a store in the first place that has a good reputation. You can see your shop's reputation with a particular class at [Potion Exchange](https://potion-exchange.vercel.app/). Reputation is based on three different factors:
1. Value: Value is calculated as the delta between the utility the customer gets from a potion (which is increased by getting as close to possible to that customer's preference) and how much the store charges. The highest value is achieved by offering cheap potions that exactly match a customer's preference.
2. Reliability: Reliability is based upon not having errors in the checkout process. Your site being down or offering up potions for sale you don't have in inventory are examples of errors that will hurt reliability.
3. Recognition: Recognition is based upon the number of total successful purchasing trips that customers of that class have had. The more you serve a particular class, the more others of that class will trust to come to you.

For more information please reference the [API Spec](APISpec.md)
