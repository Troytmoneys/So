import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# User data and leaderboard tracking
user_data = {}

# Coffee types
coffee_types = [
    "Espresso", "Double Espresso", "Red Eye", "Black Eye", "Americano", "Long Black",
    "Macchiato", "Long Macchiato", "Cortado", "Breve", "Cappuccino", "Flat White",
    "Cafe Latte", "Mocha", "Vienna", "Affogato", "Cafe au Lait", "Iced Coffee"
]

# Command to show coffee types
@bot.command(name='coffee')
async def coffee(ctx):
    embed = discord.Embed(title="Choose your coffee type", description="\n".join(f"{i+1}. {ct}" for i, ct in enumerate(coffee_types)), color=0x00ff00)
    view = View(timeout=None)
    for i, coffee in enumerate(coffee_types):
        button = Button(label=coffee, custom_id=f"coffee_{i}", style=discord.ButtonStyle.primary)
        button.callback = lambda interaction, c=coffee: coffee_selection_callback(interaction, c, ctx.author)
        view.add_item(button)
    await ctx.send(embed=embed, view=view)

async def coffee_selection_callback(interaction, coffee, user):
    # Initialize or update user data
    if user.id not in user_data:
        user_data[user.id] = {'coffees': []}
    user_coffee = {'type': coffee, 'beans': 0, 'milk': False}
    user_data[user.id]['coffees'].append(user_coffee)

    # Confirmation message
    await interaction.response.send_message(f"You selected {coffee}. Preparing customization options...", ephemeral=True)
    await asyncio.sleep(5)  # Wait for 5 seconds before next step

    # Proceed to customization
    await send_customization_options(interaction, user_coffee, user)

async def send_customization_options(interaction, coffee_data, user):
    embed = discord.Embed(title="Customize Your Coffee", description="Select number of beans", color=0x0000ff)
    view = View(timeout=30)

    # Bean selection buttons
    for i in range(1, 4):
        button = Button(label=str(i), style=discord.ButtonStyle.secondary)
        button.callback = lambda inter, b=i: beans_selection_callback(inter, coffee_data, b, user)
        view.add_item(button)
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def beans_selection_callback(interaction, coffee_data, beans, user):
    # Update coffee data
    coffee_data['beans'] = beans
    embed = discord.Embed(title="Beans Added", description=f"{beans} beans added to your {coffee_data['type']}.", color=0xff0000)
    await interaction.response.edit_message(embed=embed, view=None)

    # Ask for milk
    embed = discord.Embed(title="Would you like to add milk?", description="Select yes or no.", color=0x0000ff)
    view = View(timeout=30)
    yes_button = Button(label="Yes", style=discord.ButtonStyle.success)
    no_button = Button(label="No", style=discord.ButtonStyle.danger)
    yes_button.callback = lambda inter: milk_selection_callback(inter, coffee_data, True, user)
    no_button.callback = lambda inter: milk_selection_callback(inter, coffee_data, False, user)
    view.add_item(yes_button)
    view.add_item(no_button)
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def milk_selection_callback(interaction, coffee_data, milk, user):
  # Update coffee data
  coffee_data['milk'] = milk
  milk_status = "with milk" if milk else "without milk"
  embed = discord.Embed(title="Milk Added", description=f"Milk has been added: {milk_status}.", color=0x0000ff)
  await interaction.response.edit_message(embed=embed, view=None)

  # Confirm final selection
  final_embed = discord.Embed(
      title="Coffee Ready",
      description=f"Your {coffee_data['type']} {milk_status} and {coffee_data['beans']} beans is ready!",
      color=0x00ff00
  )
  await interaction.followup.send(embed=final_embed, ephemeral=True)

# Command to view profile
# Command to view profile
@bot.command(name='profile')
async def profile(ctx):
    user_coffees = user_data.get(ctx.author.id, {}).get('coffees', [])
    if user_coffees:
        description = "\n".join(f"{c['type']}: Beans {c['beans']}, Milk {'Yes' if c['milk'] else 'No'}" for c in user_coffees)
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Coffee History", description=description, color=0x0000ff)
    else:
        embed = discord.Embed(title="No Coffee History", description="You haven't made any coffee yet!", color=0xff0000)
    await ctx.send(embed="Command to view leaderboard")
# Command to view leaderboard
@bot.command(name='leaderboard')
async def leaderboard(ctx):
    # Generate leaderboard from user data
    leaderboard_data = {user_id: len(data['coffees']) for user_id, data in user_data.items()}
    sorted_leaderboard = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)[:10]

    # Format leaderboard message
    leaderboard_entries = []
    for user_id, count in sorted_leaderboard:
        user = await bot.fetch_user(user_id)
        leaderboard_entries.append(f"{user.display_name}: {count} coffees")

    description = "\n".join(leaderboard_entries)
    embed = discord.Embed(title="Coffee Leaderboard", description=description, color=0x00ff00)
    await ctx.send(embed=embed)

# Command to ping
@bot.command(name='ping')
async def ping(ctx):
  await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

# Run the bot
bot.run('your_bot_token')
