import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import asyncio

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Setup logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Data storage (in a real application, you'd use a database)
class ProjectManager:
    def __init__(self):
        self.projects = {}
        self.user_roles = {}
        self.user_points = {}
        self.user_tasks = {}
        self.shop_items = {
            "Custom Role": 1000,
            "Server Boost": 500,
            "Special Badge": 300,
            "Priority Support": 200,
            "Custom Emoji": 150
        }
        self.available_tasks = {
            "Complete a project": 50,
            "Help a team member": 25,
            "Submit bug report": 30,
            "Write documentation": 40,
            "Code review": 35
        }
        self.load_data()
    
    def load_data(self):
        try:
            with open('project_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.projects = data.get('projects', {})
                self.user_roles = data.get('user_roles', {})
                self.user_points = data.get('user_points', {})
                self.user_tasks = data.get('user_tasks', {})
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load data file: {e}")
            # Initialize with default values
            self.projects = {}
            self.user_roles = {}
            self.user_points = {}
            self.user_tasks = {}
    
    def save_data(self):
        try:
            data = {
                'projects': self.projects,
                'user_roles': self.user_roles,
                'user_points': self.user_points,
                'user_tasks': self.user_tasks
            }
            with open('project_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error saving data: {e}")

# Initialize project manager
pm = ProjectManager()

@bot.event
async def on_ready():
    if bot.user:
        print(f"{bot.user.name} is online and ready for project management!")
        print(f"Bot ID: {bot.user.id}")
        print(f"Connected to {len(bot.guilds)} guild(s)")
    else:
        print("Bot is online but user information is not available.")

@bot.command(name='commands')
async def help_command(ctx):
    """Shows all available commands"""
    embed = discord.Embed(
        title="🤖 Project Management Bot Commands",
        description="Here are all the available commands with their syntax:",
        color=0x00ff00
    )
    
    commands_info = {
        "!commands": "Shows this help message with command syntax",
        "!roles": "Shows all available roles in the server that you can assign to yourself",
        "!role assign <role_name>": "Assigns a role to yourself\n**Syntax:** `!role assign Developer`",
        "!role remove <role_name>": "Removes a role from yourself\n**Syntax:** `!role remove Developer`",
        "!nickname <name> <profession>": "Changes your nickname to include your name and profession\n**Syntax:** `!nickname John Developer`",
        "!projects": "Shows all ongoing projects in the server",
        "!project <name> dashboard": "Shows the dashboard for a specific project\n**Syntax:** `!project MyProject dashboard`",
        "!project <name> progress": "Shows the progress of a specific project\n**Syntax:** `!project MyProject progress`",
        "!project <name> details": "Shows detailed information about a project\n**Syntax:** `!project MyProject details`",
        "!project <name> assign <task>": "Assigns a task to yourself and creates the project if it doesn't exist\n**Syntax:** `!project MyProject assign Fix the login bug`",
        "!rewards": "Shows your current points and available tasks you can complete",
        "!shop": "Shows items you can purchase with your earned points"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=f"📝 {cmd}", value=desc, inline=False)
    
    embed.add_field(
        name="💡 Tips",
        value="• Project names are case-sensitive\n• Tasks can contain spaces and special characters\n• You earn 25 points for each task you assign\n• Nicknames are limited to 32 characters\n• Use `!commands` anytime to see this help message",
        inline=False
    )
    
    embed.set_footer(text="Use these commands to manage your projects effectively!")
    await ctx.send(embed=embed)

@bot.command(name='roles')
async def show_roles(ctx):
    """Shows available roles in the server"""
    try:
        roles = [role.name for role in ctx.guild.roles if role.name != "@everyone" and not role.managed]
        
        embed = discord.Embed(
            title="🏷️ Available Roles",
            description="Roles you can assign to yourself:",
            color=0x0099ff
        )
        
        if roles:
            # Limit roles to prevent embed overflow
            roles_text = "\n".join([f"• {role}" for role in roles[:25]])
            if len(roles) > 25:
                roles_text += f"\n... and {len(roles) - 25} more roles"
            embed.add_field(name="Roles", value=roles_text, inline=False)
        else:
            embed.add_field(name="Roles", value="No assignable roles available", inline=False)
        
        embed.add_field(
            name="How to assign", 
            value="Use `!role assign <role_name>` to assign a role to yourself", 
            inline=False
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing roles: {str(e)}")

@bot.command(name='role')
async def role_command(ctx, action, *, role_name):
    """Assigns or removes a role from the user"""
    if not action or action.lower() not in ['assign', 'remove']:
        await ctx.send("❌ Invalid action. Use `!role assign <role_name>` or `!role remove <role_name>`")
        return
    
    if not role_name or role_name.strip() == "":
        await ctx.send("❌ Please specify a role name!")
        return
    
    try:
        # Find the role
        role = discord.utils.get(ctx.guild.roles, name=role_name.strip())
        
        if not role:
            await ctx.send(f"❌ Role '{role_name}' not found!")
            return
        
        if action.lower() == 'assign':
            # Check if user already has the role
            if role in ctx.author.roles:
                await ctx.send(f"❌ You already have the role '{role_name}'!")
                return
            
            # Check if bot has permission to manage roles
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.send("❌ I don't have permission to manage roles!")
                return
            
            # Check if the role is manageable (not higher than bot's role)
            if role >= ctx.guild.me.top_role:
                await ctx.send("❌ I can't assign that role because it's higher than my highest role!")
                return
            
            await ctx.author.add_roles(role)
            pm.user_roles[str(ctx.author.id)] = role_name
            pm.save_data()
            
            embed = discord.Embed(
                title="✅ Role Assigned!",
                description=f"You have been assigned the role: **{role_name}**",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        elif action.lower() == 'remove':
            # Check if user has the role
            if role not in ctx.author.roles:
                await ctx.send(f"❌ You don't have the role '{role_name}'!")
                return
            
            # Check if bot has permission to manage roles
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.send("❌ I don't have permission to manage roles!")
                return
            
            # Check if the role is manageable (not higher than bot's role)
            if role >= ctx.guild.me.top_role:
                await ctx.send("❌ I can't remove that role because it's higher than my highest role!")
                return
            
            await ctx.author.remove_roles(role)
            
            # Remove from stored data if exists
            user_id = str(ctx.author.id)
            if user_id in pm.user_roles and pm.user_roles[user_id] == role_name:
                del pm.user_roles[user_id]
                pm.save_data()
            
            embed = discord.Embed(
                title="✅ Role Removed!",
                description=f"The role **{role_name}** has been removed from you",
                color=0xff6b6b
            )
            await ctx.send(embed=embed)
            
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to manage that role!")
    except Exception as e:
        await ctx.send(f"❌ Error managing role: {str(e)}")

@bot.command(name='nickname')
async def change_nickname(ctx, name, *, profession):
    """Changes the user's nickname to include their name and profession"""
    if not name or name.strip() == "":
        await ctx.send("❌ Please provide your name! Usage: `!nickname <name> <profession>`")
        return
    
    if not profession or profession.strip() == "":
        await ctx.send("❌ Please provide your profession! Usage: `!nickname <name> <profession>`")
        return
    
    try:
        # Check if bot has permission to manage nicknames
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            await ctx.send("❌ I don't have permission to change nicknames!")
            return
        
        # Create the new nickname
        new_nickname = f"{name.strip()} | {profession.strip()}"
        
        # Limit nickname length (Discord limit is 32 characters)
        if len(new_nickname) > 32:
            # Truncate profession if needed
            max_name_length = len(name.strip()) + 3  # +3 for " | "
            max_profession_length = 32 - max_name_length
            if max_profession_length > 0:
                new_nickname = f"{name.strip()} | {profession.strip()[:max_profession_length]}"
            else:
                # If name is too long, just use the name
                new_nickname = name.strip()[:32]
        
        await ctx.author.edit(nick=new_nickname)
        
        embed = discord.Embed(
            title="✅ Nickname Updated!",
            description=f"Your nickname has been changed to: **{new_nickname}**",
            color=0x00ff00
        )
        embed.add_field(name="Name", value=name.strip(), inline=True)
        embed.add_field(name="Profession", value=profession.strip(), inline=True)
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change your nickname!")
    except Exception as e:
        await ctx.send(f"❌ Error changing nickname: {str(e)}")

@bot.command(name='projects')
async def show_projects(ctx):
    """Shows all ongoing projects"""
    try:
        if not pm.projects:
            embed = discord.Embed(
                title="📋 Projects",
                description="No projects found. Create a project by assigning a task with `!project <name> assign <task>`!",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Ongoing Projects",
            description="Here are all the projects:",
            color=0x0099ff
        )
        
        for project_name, project_data in pm.projects.items():
            status = project_data.get('status', 'In Progress')
            progress = project_data.get('progress', 0)
            task_count = len(project_data.get('tasks', []))
            embed.add_field(
                name=f"📁 {project_name}",
                value=f"Status: {status}\nProgress: {progress}%\nTasks: {task_count}",
                inline=True
            )
        
        embed.add_field(
            name="How to view details",
            value="Use `!project <name> dashboard` to see project details",
            inline=False
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing projects: {str(e)}")

@bot.command(name='project')
async def project_command(ctx, project_name=None, action=None, *, task_description=None):
    """Handles project-related commands"""
    if not project_name:
        await ctx.send("❌ Please specify a project name! Usage: `!project <name> <action>`")
        return
    
    if not action:
        await ctx.send("❌ Please specify an action! Use: dashboard, progress, details, or assign")
        return
    
    # Validate project name (basic validation)
    if len(project_name) > 50:
        await ctx.send("❌ Project name is too long! Please use a shorter name.")
        return
    
    try:
        if action.lower() == 'dashboard':
            await show_project_dashboard(ctx, project_name)
        elif action.lower() == 'progress':
            await show_project_progress(ctx, project_name)
        elif action.lower() == 'details':
            await show_project_details(ctx, project_name)
        elif action.lower() == 'assign':
            if not task_description or task_description.strip() == "":
                await ctx.send("❌ Please specify a task to assign!")
                return
            await assign_task(ctx, project_name, task_description.strip())
        else:
            await ctx.send("❌ Invalid action. Use: dashboard, progress, details, or assign")
    except Exception as e:
        await ctx.send(f"❌ Error processing project command: {str(e)}")

async def show_project_dashboard(ctx, project_name):
    """Shows project dashboard"""
    if project_name not in pm.projects:
        await ctx.send(f"❌ Project '{project_name}' not found!")
        return
    
    try:
        project = pm.projects[project_name]
        
        embed = discord.Embed(
            title=f"📊 {project_name} Dashboard",
            description=project.get('description', 'No description available')[:2000],  # Limit description length
            color=0x00ff00
        )
        
        embed.add_field(name="Status", value=project.get('status', 'In Progress'), inline=True)
        embed.add_field(name="Progress", value=f"{project.get('progress', 0)}%", inline=True)
        embed.add_field(name="Created", value=project.get('created', 'Unknown'), inline=True)
        
        tasks = project.get('tasks', [])
        if tasks:
            task_text = "\n".join([f"• {task}" for task in tasks[:5]])
            if len(tasks) > 5:
                task_text += f"\n... and {len(tasks) - 5} more tasks"
            embed.add_field(name="Recent Tasks", value=task_text[:1024], inline=False)  # Limit field length
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing project dashboard: {str(e)}")

async def show_project_progress(ctx, project_name):
    """Shows project progress"""
    if project_name not in pm.projects:
        await ctx.send(f"❌ Project '{project_name}' not found!")
        return
    
    try:
        project = pm.projects[project_name]
        progress = project.get('progress', 0)
        
        # Create a progress bar
        bar_length = 20
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        embed = discord.Embed(
            title=f"📈 {project_name} Progress",
            description=f"Progress: {progress}%",
            color=0x00ff00
        )
        
        embed.add_field(name="Progress Bar", value=f"`{bar}`", inline=False)
        embed.add_field(name="Status", value=project.get('status', 'In Progress'), inline=True)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing project progress: {str(e)}")

async def show_project_details(ctx, project_name):
    """Shows detailed project information"""
    if project_name not in pm.projects:
        await ctx.send(f"❌ Project '{project_name}' not found!")
        return
    
    try:
        project = pm.projects[project_name]
        
        embed = discord.Embed(
            title=f"📋 {project_name} Details",
            description=project.get('description', 'No description available')[:2000],  # Limit description length
            color=0x0099ff
        )
        
        embed.add_field(name="Status", value=project.get('status', 'In Progress'), inline=True)
        embed.add_field(name="Progress", value=f"{project.get('progress', 0)}%", inline=True)
        embed.add_field(name="Created", value=project.get('created', 'Unknown'), inline=True)
        
        tasks = project.get('tasks', [])
        if tasks:
            task_text = "\n".join([f"• {task}" for task in tasks])
            embed.add_field(name="All Tasks", value=task_text[:1024], inline=False)  # Limit field length
        
        members = project.get('members', [])
        if members:
            member_text = "\n".join([f"• {member}" for member in members])
            embed.add_field(name="Team Members", value=member_text[:1024], inline=False)  # Limit field length
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing project details: {str(e)}")

async def assign_task(ctx, project_name, task_description):
    """Assigns a task to the user"""
    try:
        if project_name not in pm.projects:
            # Create new project if it doesn't exist
            pm.projects[project_name] = {
                'description': f'Project created by {ctx.author.name}',
                'status': 'In Progress',
                'progress': 0,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tasks': [],
                'members': []
            }
        
        project = pm.projects[project_name]
        
        # Add task
        if 'tasks' not in project:
            project['tasks'] = []
        
        project['tasks'].append(task_description)
        
        # Add member if not already there
        if 'members' not in project:
            project['members'] = []
        
        if ctx.author.name not in project['members']:
            project['members'].append(ctx.author.name)
        
        # Update progress
        project['progress'] = min(100, project['progress'] + 10)
        
        # Award points to user
        user_id = str(ctx.author.id)
        if user_id not in pm.user_points:
            pm.user_points[user_id] = 0
        pm.user_points[user_id] += 25  # Award 25 points for task assignment
        
        pm.save_data()
        
        embed = discord.Embed(
            title="✅ Task Assigned!",
            description=f"Task assigned to project: **{project_name}**",
            color=0x00ff00
        )
        embed.add_field(name="Task", value=task_description[:1024], inline=False)  # Limit field length
        embed.add_field(name="Assigned by", value=ctx.author.mention, inline=True)
        embed.add_field(name="New Progress", value=f"{project['progress']}%", inline=True)
        embed.add_field(name="Points Earned", value="+25 points", inline=True)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error assigning task: {str(e)}")

@bot.command(name='rewards')
async def show_rewards(ctx):
    """Shows user's current points and available tasks"""
    try:
        user_id = str(ctx.author.id)
        points = pm.user_points.get(user_id, 0)
        
        embed = discord.Embed(
            title="🏆 Your Rewards",
            description=f"Current Points: **{points}**",
            color=0xffd700
        )
        
        embed.add_field(
            name="Available Tasks",
            value="Complete these tasks to earn points:",
            inline=False
        )
        
        for task, points_reward in pm.available_tasks.items():
            embed.add_field(name=task, value=f"Reward: {points_reward} points", inline=True)
        
        embed.add_field(
            name="How to earn points",
            value="Complete tasks and help with projects to earn points!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing rewards: {str(e)}")

@bot.command(name='shop')
async def show_shop(ctx):
    """Shows items available in the shop"""
    try:
        user_id = str(ctx.author.id)
        points = pm.user_points.get(user_id, 0)
        
        embed = discord.Embed(
            title="🛒 Points Shop",
            description=f"Your current points: **{points}**",
            color=0xff6b6b
        )
        
        embed.add_field(
            name="Available Items",
            value="Items you can purchase with points:",
            inline=False
        )
        
        for item, cost in pm.shop_items.items():
            can_afford = "✅" if points >= cost else "❌"
            embed.add_field(
                name=f"{can_afford} {item}",
                value=f"Cost: {cost} points",
                inline=True
            )
        
        embed.add_field(
            name="How to purchase",
            value="Contact an administrator to purchase items with your points!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing shop: {str(e)}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `!commands` to see command usage.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!commands` to see available commands.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided. Use `!commands` to see command usage.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    if not token:
        print("❌ Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        exit(1)
    
    try:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    except discord.LoginFailure:
        print("❌ Error: Invalid Discord bot token!")
        print("Please check your .env file and make sure the token is correct.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

