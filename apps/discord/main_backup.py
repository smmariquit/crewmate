import discord
from discord.ext import commands
from discord import app_commands
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

# Slash command autocomplete data
COMMAND_SUGGESTIONS = {
    'project': ['dashboard', 'details', 'assign'],
    'role': ['assign', 'remove'],
    'shop': ['add'],
    'perm': ['add', 'remove', 'view'],
    'completed': ['project'],
    'new': ['project'],
    'edit': ['project'],
    'delete': ['project'],
    'forums': []
}

PROJECT_NAMES = []  # Will be populated dynamically

# Data storage (in a real application, you'd use a database)
class ProjectManager:
    def __init__(self):
        self.projects = {}
        self.user_roles = {}
        self.user_points = {}
        self.user_tasks = {}
        self.forum_channel_name = "📋・projects"  # Default forum channel
        self.permissions = {
            'project_management': ['owner', 'admin', 'Team Leader'],  # new, edit, delete project
            'forum_config': ['owner', 'admin'],  # project forums
            'shop_management': ['owner', 'admin'],  # shop add
            'permission_management': ['owner']  # perm command
        }
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
                self.forum_channel_name = data.get('forum_channel_name', "📋・projects")
                self.permissions = data.get('permissions', {
                    'project_management': ['owner', 'admin', 'Team Leader'],
                    'forum_config': ['owner', 'admin'],
                    'shop_management': ['owner', 'admin'],
                    'permission_management': ['owner']
                })
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load data file: {e}")
            # Initialize with default values
            self.projects = {}
            self.user_roles = {}
            self.user_points = {}
            self.user_tasks = {}
            self.forum_channel_name = "📋・projects"
            self.permissions = {
                'project_management': ['owner', 'admin', 'Team Leader'],
                'forum_config': ['owner', 'admin'],
                'shop_management': ['owner', 'admin'],
                'permission_management': ['owner']
            }
    
    def save_data(self):
        try:
            data = {
                'projects': self.projects,
                'user_roles': self.user_roles,
                'user_points': self.user_points,
                'user_tasks': self.user_tasks,
                'forum_channel_name': self.forum_channel_name,
                'permissions': self.permissions
            }
            with open('project_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error saving data: {e}")
    
    def has_permission(self, user_roles, permission_type):
        """Check if user has permission for a specific action"""
        required_roles = self.permissions.get(permission_type, [])
        return any(role in user_roles for role in required_roles)

# Initialize project manager
pm = ProjectManager()

def update_project_names():
    """Updates the PROJECT_NAMES list for autocomplete"""
    global PROJECT_NAMES
    PROJECT_NAMES = list(pm.projects.keys())

# Autocomplete functions for slash commands
async def project_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for project names"""
    update_project_names()
    choices = []
    for project_name in PROJECT_NAMES:
        if current.lower() in project_name.lower():
            choices.append(app_commands.Choice(name=project_name, value=project_name))
    return choices[:25]  # Discord limit

async def action_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for project actions"""
    actions = ['dashboard', 'details', 'assign']
    choices = []
    for action in actions:
        if current.lower() in action.lower():
            choices.append(app_commands.Choice(name=action, value=action))
    return choices[:25]

async def role_action_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for role actions"""
    actions = ['assign', 'remove']
    choices = []
    for action in actions:
        if current.lower() in action.lower():
            choices.append(app_commands.Choice(name=action, value=action))
    return choices[:25]

async def perm_action_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for permission actions"""
    actions = ['add', 'remove', 'view']
    choices = []
    for action in actions:
        if current.lower() in action.lower():
            choices.append(app_commands.Choice(name=action, value=action))
    return choices[:25]

async def shop_action_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for shop actions"""
    actions = ['add']
    choices = []
    for action in actions:
        if current.lower() in action.lower():
            choices.append(app_commands.Choice(name=action, value=action))
    return choices[:25]

@bot.event
async def on_ready():
    if bot.user:
        print(f"{bot.user.name} is online and ready for project management!")
        print(f"Bot ID: {bot.user.id}")
        print(f"Connected to {len(bot.guilds)} guild(s)")
    else:
        print("Bot is online but user information is not available.")

@bot.event
async def on_member_join(member):
    """Greets new members and assigns them the member role"""
    try:
        # Find the member role
        member_role = discord.utils.get(member.guild.roles, name="Member")
        
        if member_role:
            # Check if bot has permission to manage roles
            if member.guild.me.guild_permissions.manage_roles:
                # Check if the role is manageable (not higher than bot's role)
                if member_role < member.guild.me.top_role:
                    await member.add_roles(member_role)
                    
                    # Create welcome embed
                    embed = discord.Embed(
                        title="🎉 Welcome to the Server!",
                        description=f"Hello {member.mention}! Welcome to our project management community!",
                        color=0x00ff00
                    )
                    embed.add_field(
                        name="✅ Role Assigned",
                        value="You have been automatically assigned the **Member** role!",
                        inline=False
                    )
                    embed.add_field(
                        name="🚀 Getting Started",
                        value="• Use `!commands` to see all available commands\n• Use `!roles` to see available roles\n• Use `!nickname <name> <profession>` to set your nickname\n• Start managing projects with `!project <name> assign <task>`",
                        inline=False
                    )
                    embed.add_field(
                        name="💡 Quick Tips",
                        value="• Assign yourself roles with `!role assign <role_name>`\n• Check your rewards with `!rewards`\n• View projects with `!projects`",
                        inline=False
                    )
                    embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else member.default_avatar.url)
                    embed.set_footer(text="Enjoy your time in our community!")
                    
                    # Try to send to a general channel or the first available text channel
                    general_channel = discord.utils.get(member.guild.text_channels, name="general")
                    if general_channel:
                        await general_channel.send(embed=embed)
                    else:
                        # Send to the first available text channel
                        for channel in member.guild.text_channels:
                            if channel.permissions_for(member.guild.me).send_messages:
                                await channel.send(embed=embed)
                                break
                else:
                    print(f"Warning: Cannot assign Member role to {member.name} - role is higher than bot's role")
            else:
                print(f"Warning: Bot doesn't have permission to manage roles for {member.name}")
        else:
            print(f"Warning: 'Member' role not found in guild {member.guild.name}")
            
    except Exception as e:
        print(f"Error welcoming new member {member.name}: {str(e)}")

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
        "!project <name> details": "Shows detailed information about a project\n**Syntax:** `!project MyProject details`",
        "!project <name> assign": "Assigns yourself to a predefined task in a project\n**Syntax:** `!project MyProject assign`\n**Note:** The bot will list available tasks and let you select by number",
        "!forums <channel>": "Configures the forum channel for project posts (Owner/Admin only)",
        "!new project": "Creates a new project with predefined tasks (Owner/Admin/Team Leader only)",
        "!edit project <name>": "Edits an existing project (Owner/Admin/Team Leader only)",
        "!delete project <name>": "Deletes a project (Owner/Admin/Team Leader only)",
        "!rewards": "Shows your current points and available tasks you can complete",
        "!shop": "Shows items you can purchase with your earned points",
        "!shop add <item> <price>": "Adds a new item to the shop (Owner/Admin only)",
        "!completed project <name>": "Marks a task as completed and rewards users\n**Syntax:** `!completed project MyProject`\n**Note:** The bot will list your assigned tasks and let you select by number",
        "!perm add <role>": "Grants all permissions to a role (Server Owner only)",
        "!perm remove <role>": "Removes all permissions from a role (Server Owner only)",
        "!perm view <role>": "Shows current permissions for a role (Server Owner only)"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=f"📝 {cmd}", value=desc, inline=False)
    
    embed.add_field(
        name="💡 Tips",
        value="• Project names are case-sensitive\n• Tasks can contain spaces and special characters\n• Nicknames are limited to 32 characters\n• Use `!commands` anytime to see this help message",
        inline=False
    )
    
    # Add quick command suggestions
    update_project_names()
    if PROJECT_NAMES:
        project_examples = PROJECT_NAMES[:3]  # Show first 3 projects as examples
        embed.add_field(
            name="🚀 Quick Start Examples",
            value=f"Try these commands:\n• `!project {project_examples[0]} dashboard`\n• `!project {project_examples[0]} assign`\n• `!completed project {project_examples[0]}`",
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
                description="No projects found. Create a project using `!new project`!",
                color=0xff9900
            )
            embed.add_field(
                name="How to create a project",
                value="Use `!new project` to create a new project with tasks and rewards.",
                inline=False
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
async def project_command(ctx, *, args=None):
    """Handles project-related commands"""
    if not args:
        await ctx.send("❌ Please specify a project name and action! Usage: `!project <name> <action>`")
        return
    
    # Parse the arguments to handle project names with spaces
    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Please specify both project name and action! Usage: `!project <name> <action>`")
        return
    
    # Find the action (last word) and project name (everything before it)
    action = parts[-1].lower()
    project_name = ' '.join(parts[:-1])
    
    # Validate project name (basic validation)
    if len(project_name) > 50:
        await ctx.send("❌ Project name is too long! Please use a shorter name.")
        return
    
    try:
        if action == 'dashboard':
            await show_project_dashboard(ctx, project_name)
        elif action == 'details':
            await show_project_details(ctx, project_name)
        elif action == 'assign':
            # Interactive task assignment
            await assign_task_interactive(ctx, project_name)
        else:
            await ctx.send("❌ Invalid action. Use: dashboard, details, or assign")
    except Exception as e:
        await ctx.send(f"❌ Error processing project command: {str(e)}")

async def show_project_dashboard(ctx, project_name):
    """Shows project dashboard"""
    if project_name not in pm.projects:
        embed = discord.Embed(
            title="❌ Project Not Found",
            description=f"Project '{project_name}' not found!",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Projects",
            value="Use `!projects` to see all available projects, or `!new project` to create a new one.",
            inline=False
        )
        await ctx.send(embed=embed)
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

async def show_project_details(ctx, project_name):
    """Shows detailed project information"""
    if project_name not in pm.projects:
        embed = discord.Embed(
            title="❌ Project Not Found",
            description=f"Project '{project_name}' not found!",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Projects",
            value="Use `!projects` to see all available projects, or `!new project` to create a new one.",
            inline=False
        )
        await ctx.send(embed=embed)
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
            embed.add_field(name="All Tasks", value=task_text[:1024], inline=False)
        
        members = project.get('members', [])
        if members:
            member_text = "\n".join([f"• {member}" for member in members])
            embed.add_field(name="Team Members", value=member_text[:1024], inline=False)  # Limit field length
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error showing project details: {str(e)}")

async def assign_task_interactive(ctx, project_name):
    """Interactive task assignment process"""
    try:
        if project_name not in pm.projects:
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project '{project_name}' not found!",
                color=0xff6b6b
            )
            embed.add_field(
                name="How to create a project",
                value="Use `!new project` to create a new project with tasks, then use `!project <name> assign` to assign yourself to tasks.",
                inline=False
            )
            embed.add_field(
                name="Available Projects",
                value="Use `!projects` to see all available projects.",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        project = pm.projects[project_name]
        
        # Check if project has the new task structure
        if not project.get('tasks') or not isinstance(project['tasks'], list):
            embed = discord.Embed(
                title="❌ Invalid Project Structure",
                description=f"Project '{project_name}' doesn't have predefined tasks.",
                color=0xff6b6b
            )
            embed.add_field(
                name="How to fix",
                value="Use `!new project` to create a new project with proper task structure.",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Find available tasks (not completed and not full)
        available_tasks = []
        for i, task in enumerate(project['tasks'], 1):
            if isinstance(task, dict) and not task.get('completed', False):
                member_count = len(task.get('assigned_members', []))
                if member_count < task['max_members']:
                    available_tasks.append((i, task))
        
        if not available_tasks:
            embed = discord.Embed(
                title="❌ No Available Tasks",
                description=f"No tasks available for assignment in project '{project_name}'.",
                color=0xff6b6b
            )
            embed.add_field(
                name="Reason",
                value="All tasks are either completed or have reached their maximum member limit.",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Show available tasks
        embed = discord.Embed(
            title=f"📋 Available Tasks in {project_name}",
            description="Select a task to assign yourself to by typing its number, or type 'exit' to cancel:",
            color=0x0099ff
        )
        
        task_list = []
        for task_num, task in available_tasks:
            member_count = len(task.get('assigned_members', []))
            task_list.append(f"{task_num}. **{task['description']}** (Reward: {task['reward_points']} points, Members: {member_count}/{task['max_members']})")
        
        embed.add_field(name="Available Tasks", value="\n".join(task_list), inline=False)
        embed.add_field(name="Instructions", value="Type the number of the task you want to work on, or 'exit' to cancel.", inline=False)
        
        await ctx.send(embed=embed)
        
        # Wait for user response
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            response = await bot.wait_for('message', timeout=60.0, check=check)
            choice = response.content.strip().lower()
            
            if choice == 'exit':
                await ctx.send("❌ Task assignment cancelled.")
                return
            
            try:
                task_index = int(choice) - 1  # Convert to 0-based index
                if task_index < 0 or task_index >= len(project['tasks']):
                    await ctx.send("❌ Invalid task number! Please try again.")
                    return
                
                # Find the selected task
                selected_task = None
                for i, task in enumerate(project['tasks']):
                    if isinstance(task, dict) and not task.get('completed', False):
                        member_count = len(task.get('assigned_members', []))
                        if member_count < task['max_members'] and i == task_index:
                            selected_task = task
                            break
                
                if not selected_task:
                    await ctx.send("❌ Invalid task selection! Please try again.")
                    return
                
                # Check if user is already assigned to this task
                user_id = str(ctx.author.id)
                if user_id in selected_task.get('assigned_members', []):
                    await ctx.send(f"❌ You are already assigned to task '{selected_task['description']}'!")
                    return
                
                # Check if task has reached maximum members
                if len(selected_task.get('assigned_members', [])) >= selected_task['max_members']:
                    await ctx.send(f"❌ Task '{selected_task['description']}' has reached its maximum number of members ({selected_task['max_members']})!")
                    return
                
                # Assign user to task
                if 'assigned_members' not in selected_task:
                    selected_task['assigned_members'] = []
                selected_task['assigned_members'].append(user_id)
                
                # Add member to project if not already there
                if 'members' not in project:
                    project['members'] = []
                
                if ctx.author.name not in project['members']:
                    project['members'].append(ctx.author.name)
                
                # Update project progress
                total_tasks = len(project['tasks'])
                completed_tasks = sum(1 for task in project['tasks'] if isinstance(task, dict) and task.get('completed', False))
                project['progress'] = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
                
                pm.save_data()
                
                embed = discord.Embed(
                    title="✅ Task Assigned!",
                    description=f"Task assigned to project: **{project_name}**",
                    color=0x00ff00
                )
                embed.add_field(name="Task", value=selected_task['description'][:1024], inline=False)
                embed.add_field(name="Assigned by", value=ctx.author.mention, inline=True)
                embed.add_field(name="Reward", value=f"{selected_task['reward_points']} points", inline=True)
                embed.add_field(name="Members", value=f"{len(selected_task['assigned_members'])}/{selected_task['max_members']}", inline=True)
                embed.add_field(name="Project Progress", value=f"{project['progress']}%", inline=True)
                
                await ctx.send(embed=embed)
                
                # Update forum post
                await update_forum_post(project_name, project)
                
            except ValueError:
                await ctx.send("❌ Please enter a valid number or 'exit' to cancel.")
                return
                
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timeout! Task assignment cancelled.")
            return
        
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
async def shop_command(ctx, action=None, *, item_info=None):
    """Handles shop-related commands"""
    if action is None:
        # Show shop items (existing functionality)
        await show_shop(ctx)
        return
    
    if action.lower() == 'add':
        # Check if user has required roles
        user_roles = [role.name for role in ctx.author.roles]
        if not pm.has_permission(user_roles, 'shop_management'):
            await ctx.send("❌ You don't have permission to add shop items. Contact an administrator to configure permissions.")
            return
        
        if not item_info:
            await ctx.send("❌ Please specify an item and price! Usage: `!shop add <item> <price>`")
            return
        
        # Parse item and price
        try:
            # Split by last space to separate item name and price
            parts = item_info.rsplit(' ', 1)
            if len(parts) != 2:
                await ctx.send("❌ Invalid format! Use: `!shop add <item name> <price>`")
                return
            
            item_name = parts[0].strip()
            price = int(parts[1])
            
            if price <= 0:
                await ctx.send("❌ Price must be a positive number!")
                return
            
            if len(item_name) > 50:
                await ctx.send("❌ Item name is too long! Please use a shorter name (max 50 characters).")
                return
            
            # Add item to shop
            pm.shop_items[item_name] = price
            pm.save_data()
            
            embed = discord.Embed(
                title="✅ Shop Item Added!",
                description=f"New item has been added to the shop.",
                color=0x00ff00
            )
            embed.add_field(name="Item", value=item_name, inline=True)
            embed.add_field(name="Price", value=f"{price} points", inline=True)
            embed.add_field(name="Added by", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Invalid price! Price must be a number. Usage: `!shop add <item name> <price>`")
        except Exception as e:
            await ctx.send(f"❌ Error adding shop item: {str(e)}")
    
    else:
        await ctx.send("❌ Invalid shop action. Use `!shop` to view items or `!shop add <item> <price>` to add items.")

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

@bot.command(name='new')
async def new_project(ctx, project_type):
    """Creates a new project with role-based permissions"""
    if project_type.lower() != 'project':
        await ctx.send("❌ Invalid command. Use `!new project` to create a new project.")
        return
    
    # Check if user has required roles
    user_roles = [role.name for role in ctx.author.roles]
    if not pm.has_permission(user_roles, 'project_management'):
        await ctx.send("❌ You don't have permission to create projects. Contact an administrator to configure permissions.")
        return
    
    # Delete the original command message for privacy
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Send private message to user
    embed = discord.Embed(
        title="🆕 New Project Creation",
        description="Let's create a new project! I'll ask you a few questions.",
        color=0x00ff00
    )
    embed.add_field(
        name="Privacy Notice",
        value="This conversation is private. Only you can see these messages.",
        inline=False
    )
    
    await ctx.author.send(embed=embed)
    
    # Start the project creation process
    await create_project_interactive(ctx.author)

@bot.command(name='edit')
async def edit_project(ctx, project_type, *, project_name):
    """Edits an existing project with role-based permissions"""
    if project_type.lower() != 'project':
        await ctx.send("❌ Invalid command. Use `!edit project <name>` to edit a project.")
        return
    
    # Check if user has required roles
    user_roles = [role.name for role in ctx.author.roles]
    if not pm.has_permission(user_roles, 'project_management'):
        await ctx.send("❌ You don't have permission to edit projects. Contact an administrator to configure permissions.")
        return
    
    # Check if there are any projects
    if not pm.projects:
        embed = discord.Embed(
            title="❌ No Projects Found",
            description="There are no projects to edit.",
            color=0xff6b6b
        )
        embed.add_field(
            name="How to create a project",
            value="Use `!new project` to create a new project first.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Check if project exists
    if project_name not in pm.projects:
        embed = discord.Embed(
            title="❌ Project Not Found",
            description=f"Project '{project_name}' not found!",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Projects",
            value="Use `!projects` to see all available projects.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Delete the original command message for privacy
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Send private message to user
    embed = discord.Embed(
        title="✏️ Edit Project",
        description=f"Let's edit the project: **{project_name}**",
        color=0x0099ff
    )
    embed.add_field(
        name="Privacy Notice",
        value="This conversation is private. Only you can see these messages.",
        inline=False
    )
    
    await ctx.author.send(embed=embed)
    
    # Start the project editing process
    await edit_project_interactive(ctx.author, project_name)

@bot.command(name='delete')
async def delete_project(ctx, project_type, *, project_name):
    """Deletes a project with role-based permissions"""
    if project_type.lower() != 'project':
        await ctx.send("❌ Invalid command. Use `!delete project <name>` to delete a project.")
        return
    
    # Check if user has required roles
    user_roles = [role.name for role in ctx.author.roles]
    if not pm.has_permission(user_roles, 'project_management'):
        await ctx.send("❌ You don't have permission to delete projects. Contact an administrator to configure permissions.")
        return
    
    # Check if there are any projects
    if not pm.projects:
        embed = discord.Embed(
            title="❌ No Projects Found",
            description="There are no projects to delete.",
            color=0xff6b6b
        )
        embed.add_field(
            name="How to create a project",
            value="Use `!new project` to create a new project first.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Check if project exists
    if project_name not in pm.projects:
        embed = discord.Embed(
            title="❌ Project Not Found",
            description=f"Project '{project_name}' not found!",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Projects",
            value="Use `!projects` to see all available projects.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Delete the original command message for privacy
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Send private message to user
    embed = discord.Embed(
        title="🗑️ Delete Project",
        description=f"Are you sure you want to delete the project: **{project_name}**?",
        color=0xff6b6b
    )
    embed.add_field(
        name="Warning",
        value="This action cannot be undone! All project data will be permanently deleted.",
        inline=False
    )
    embed.add_field(
        name="Privacy Notice",
        value="This conversation is private. Only you can see these messages.",
        inline=False
    )
    
    await ctx.author.send(embed=embed)
    
    # Start the project deletion process
    await delete_project_interactive(ctx.author, project_name)

async def create_project_interactive(user):
    """Interactive project creation process"""
    try:
        # Check if forum channel is configured and accessible
        forum_channel = None
        configured_channel_name = pm.forum_channel_name
        
        for guild in bot.guilds:
            # First try to find the configured channel
            channel = discord.utils.get(guild.channels, name=configured_channel_name)
            if channel:
                # Check if it's actually a forum channel
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    forum_channel = channel
                    break
                else:
                    # Channel exists but it's not a forum channel
                    embed = discord.Embed(
                        title="❌ Invalid Channel Type",
                        description=f"Channel '{configured_channel_name}' exists but is not a forum channel.",
                        color=0xff6b6b
                    )
                    embed.add_field(
                        name="Problem",
                        value=f"The configured channel '{configured_channel_name}' is a {channel.type.name} channel, not a forum channel.",
                        inline=False
                    )
                    embed.add_field(
                        name="How to fix",
                        value="1. Create a new forum channel in your server\n2. Use `!project forums <forum_channel_name>` to configure it",
                        inline=False
                    )
                    await user.send(embed=embed)
                    return
            else:
                # Check if there are any forum channels in the guild
                forum_channels = [ch for ch in guild.channels if hasattr(ch, 'type') and ch.type == discord.ChannelType.forum]
                if forum_channels:
                    embed = discord.Embed(
                        title="❌ Forum Channel Not Configured",
                        description=f"Could not find forum channel: '{configured_channel_name}'",
                        color=0xff6b6b
                    )
                    embed.add_field(
                        name="Available Forum Channels",
                        value="Here are the forum channels in this server:",
                        inline=False
                    )
                    
                    channels_text = "\n".join([f"• {forum.name}" for forum in forum_channels[:10]])
                    if len(forum_channels) > 10:
                        channels_text += f"\n... and {len(forum_channels) - 10} more"
                    embed.add_field(name="Forums", value=channels_text, inline=False)
                    
                    embed.add_field(
                        name="How to configure",
                        value=f"Use `!project forums <channel_name>` to set one of these forum channels for project posts.",
                        inline=False
                    )
                    embed.add_field(
                        name="Example",
                        value=f"`!project forums {forum_channels[0].name}`",
                        inline=False
                    )
                    await user.send(embed=embed)
                    return
                else:
                    # No forum channels exist in the guild
                    embed = discord.Embed(
                        title="❌ No Forum Channels Found",
                        description="This server doesn't have any forum channels.",
                        color=0xff6b6b
                    )
                    embed.add_field(
                        name="How to create a forum channel",
                        value="1. Go to your server settings\n2. Click on 'Channels' in the left sidebar\n3. Click the '+' button to create a new channel\n4. Select 'Forum' as the channel type\n5. Name it (e.g., '📋・projects')\n6. Set appropriate permissions\n7. Click 'Create Channel'",
                        inline=False
                    )
                    embed.add_field(
                        name="After creating the forum channel",
                        value="Use `!project forums <channel_name>` to configure it for project posts.",
                        inline=False
                    )
                    embed.add_field(
                        name="Note",
                        value="Forum channels are required for project management. Regular text channels cannot be used for project posts.",
                        inline=False
                    )
                    await user.send(embed=embed)
                    return
        
        if not forum_channel:
            # This should not happen if the above checks are working, but just in case
            embed = discord.Embed(
                title="❌ Forum Channel Error",
                description="Unable to find or access the configured forum channel.",
                color=0xff6b6b
            )
            embed.add_field(
                name="How to fix",
                value="Contact an administrator to configure the forum channel using `!project forums <channel_name>`",
                inline=False
            )
            await user.send(embed=embed)
            return
        
        # Check if bot has permission to create threads in the forum
        bot_member = forum_channel.guild.get_member(bot.user.id) if bot.user else None
        if not bot_member:
            embed = discord.Embed(
                title="❌ Bot Not Found in Server",
                description="The bot is not a member of this server.",
                color=0xff6b6b
            )
            await user.send(embed=embed)
            return
        
        permissions = forum_channel.permissions_for(bot_member)
        missing_permissions = []
        
        if not permissions.create_public_threads:
            missing_permissions.append("Create Public Threads")
        if not permissions.send_messages:
            missing_permissions.append("Send Messages")
        if not permissions.embed_links:
            missing_permissions.append("Embed Links")
        
        if missing_permissions:
            embed = discord.Embed(
                title="❌ Insufficient Bot Permissions",
                description=f"The bot doesn't have the required permissions in forum channel '{forum_channel.name}'",
                color=0xff6b6b
            )
            embed.add_field(
                name="Missing Permissions",
                value="\n".join([f"• {perm}" for perm in missing_permissions]),
                inline=False
            )
            embed.add_field(
                name="How to fix",
                value="Ask an administrator to grant the bot these permissions in the forum channel:",
                inline=False
            )
            embed.add_field(
                name="Required Permissions",
                value="• Send Messages\n• Create Public Threads\n• Embed Links",
                inline=False
            )
            embed.add_field(
                name="Steps",
                value="1. Right-click the forum channel\n2. Select 'Edit Channel'\n3. Go to 'Permissions' tab\n4. Add the bot role\n5. Grant the required permissions\n6. Save changes",
                inline=False
            )
            await user.send(embed=embed)
            return
        
        # Ask for project name
        await user.send("📝 **Step 1:** What is the name of the project?\n\nType 'cancel' or 'exit' to cancel project creation.")
        
        def check(m):
            return m.author == user and m.channel.type == discord.ChannelType.private
        
        try:
            name_msg = await bot.wait_for('message', timeout=60.0, check=check)
            project_name = name_msg.content.strip()
            
            if project_name.lower() in ['cancel', 'exit']:
                await user.send("❌ Project creation cancelled.")
                return
            
            if len(project_name) > 50:
                await user.send("❌ Project name is too long! Please use a shorter name (max 50 characters).")
                return
                
        except asyncio.TimeoutError:
            await user.send("⏰ Timeout! Project creation cancelled.")
            return
        
        # Ask for project description
        await user.send("📝 **Step 2:** What is the description of the project?\n\nType 'cancel' or 'exit' to cancel project creation.")
        
        try:
            desc_msg = await bot.wait_for('message', timeout=120.0, check=check)
            project_description = desc_msg.content.strip()
            
            if project_description.lower() in ['cancel', 'exit']:
                await user.send("❌ Project creation cancelled.")
                return
            
        except asyncio.TimeoutError:
            await user.send("⏰ Timeout! Project creation cancelled.")
            return
        
        # Ask for tasks
        await user.send("📝 **Step 3:** Please provide the tasks in the following format:\n`<task> <reward points> <number of members>`\n\nExample:\n`Fix login bug 50 2`\n`Update documentation 30 1`\n`Design new UI 75 3`\n\nType 'done' when finished, or 'cancel' to cancel project creation:")
        
        tasks = []
        while True:
            try:
                task_msg = await bot.wait_for('message', timeout=120.0, check=check)
                task_input = task_msg.content.strip()
                
                if task_input.lower() in ['cancel', 'exit']:
                    await user.send("❌ Project creation cancelled.")
                    return
                
                if task_input.lower() == 'done':
                    break
                
                # Parse task input
                parts = task_input.split()
                if len(parts) >= 3:
                    try:
                        reward_points = int(parts[-2])
                        num_members = int(parts[-1])
                        task_description = ' '.join(parts[:-2])
                        
                        if reward_points > 0 and num_members > 0:
                            tasks.append({
                                'description': task_description,
                                'reward_points': reward_points,
                                'max_members': num_members,
                                'assigned_members': [],
                                'completed': False
                            })
                            await user.send(f"✅ Added task: **{task_description}** (Reward: {reward_points} points, Members: {num_members})")
                        else:
                            await user.send("❌ Reward points and number of members must be positive numbers!")
                    except ValueError:
                        await user.send("❌ Invalid format! Use: `<task> <reward points> <number of members>`")
                else:
                    await user.send("❌ Invalid format! Use: `<task> <reward points> <number of members>`")
                    
            except asyncio.TimeoutError:
                await user.send("⏰ Timeout! Project creation cancelled.")
                return
        
        if not tasks:
            await user.send("❌ No tasks provided! Project creation cancelled.")
            return
        
        # Create the project
        pm.projects[project_name] = {
            'description': project_description,
            'status': 'In Progress',
            'progress': 0,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'created_by': user.name,
            'tasks': tasks,
            'members': []
        }
        
        pm.save_data()
        
        # Create forum post
        await create_forum_post(project_name, project_description, tasks, user)
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Project Created Successfully!",
            description=f"Project **{project_name}** has been created and posted to the forum.",
            color=0x00ff00
        )
        embed.add_field(name="Description", value=project_description[:1024], inline=False)
        embed.add_field(name="Tasks", value=f"{len(tasks)} tasks created", inline=True)
        embed.add_field(name="Created by", value=user.name, inline=True)
        embed.add_field(name="Forum Channel", value=forum_channel.name, inline=True)
        
        await user.send(embed=embed)
        
    except Exception as e:
        await user.send(f"❌ Error creating project: {str(e)}")

async def edit_project_interactive(user, project_name):
    """Interactive project editing process"""
    try:
        project = pm.projects[project_name]
        
        await user.send(f"📝 **Editing Project:** {project_name}\n\nWhat would you like to edit?\n1. Project description\n2. Tasks (add/remove/edit)\n3. Project status\n\nType the number (1, 2, or 3):")
        
        def check(m):
            return m.author == user and m.channel.type == discord.ChannelType.private
        
        try:
            choice_msg = await bot.wait_for('message', timeout=60.0, check=check)
            choice = choice_msg.content.strip()
            
            if choice == '1':
                await user.send("📝 Enter the new project description:")
                desc_msg = await bot.wait_for('message', timeout=120.0, check=check)
                project['description'] = desc_msg.content.strip()
                await user.send("✅ Project description updated!")
                
            elif choice == '2':
                await user.send("📝 **Task Management**\n\nWhat would you like to do?\n1. Add new task\n2. Remove task\n3. Edit task\n4. View current tasks\n\nType the number (1-4):")
                
                task_choice_msg = await bot.wait_for('message', timeout=60.0, check=check)
                task_choice = task_choice_msg.content.strip()
                
                if task_choice == '1':
                    # Add new task
                    await user.send("📝 **Adding New Task**\n\nPlease provide the task in the following format:\n`<task> <reward points> <number of members>`\n\nExample: `Fix login bug 50 2`")
                    
                    task_msg = await bot.wait_for('message', timeout=120.0, check=check)
                    task_input = task_msg.content.strip()
                    
                    # Parse task input
                    parts = task_input.split()
                    if len(parts) >= 3:
                        try:
                            reward_points = int(parts[-2])
                            num_members = int(parts[-1])
                            task_description = ' '.join(parts[:-2])
                            
                            if reward_points > 0 and num_members > 0:
                                new_task = {
                                    'description': task_description,
                                    'reward_points': reward_points,
                                    'max_members': num_members,
                                    'assigned_members': [],
                                    'completed': False
                                }
                                project['tasks'].append(new_task)
                                await user.send(f"✅ Added task: **{task_description}** (Reward: {reward_points} points, Members: {num_members})")
                            else:
                                await user.send("❌ Reward points and number of members must be positive numbers!")
                        except ValueError:
                            await user.send("❌ Invalid format! Use: `<task> <reward points> <number of members>`")
                    else:
                        await user.send("❌ Invalid format! Use: `<task> <reward points> <number of members>`")
                
                elif task_choice == '2':
                    # Remove task
                    await user.send("📝 **Current tasks:**")
                    for i, task in enumerate(project['tasks'], 1):
                        if isinstance(task, dict):
                            await user.send(f"{i}. {task['description']} (Reward: {task['reward_points']} points, Members: {task['max_members']})")
                    
                    await user.send("📝 Enter the number of the task to remove:")
                    remove_msg = await bot.wait_for('message', timeout=60.0, check=check)
                    try:
                        task_index = int(remove_msg.content.strip()) - 1
                        if 0 <= task_index < len(project['tasks']):
                            removed_task = project['tasks'].pop(task_index)
                            await user.send(f"✅ Removed task: **{removed_task['description']}**")
                        else:
                            await user.send("❌ Invalid task number!")
                    except ValueError:
                        await user.send("❌ Please enter a valid number!")
                
                elif task_choice == '3':
                    # Edit task
                    await user.send("📝 **Current tasks:**")
                    for i, task in enumerate(project['tasks'], 1):
                        if isinstance(task, dict):
                            await user.send(f"{i}. {task['description']} (Reward: {task['reward_points']} points, Members: {task['max_members']})")
                    
                    await user.send("📝 Enter the number of the task to edit:")
                    edit_msg = await bot.wait_for('message', timeout=60.0, check=check)
                    try:
                        task_index = int(edit_msg.content.strip()) - 1
                        if 0 <= task_index < len(project['tasks']):
                            task = project['tasks'][task_index]
                            await user.send(f"📝 **Editing task:** {task['description']}\n\nWhat would you like to edit?\n1. Task description\n2. Reward points\n3. Number of members\n\nType the number (1-3):")
                            
                            edit_choice_msg = await bot.wait_for('message', timeout=60.0, check=check)
                            edit_choice = edit_choice_msg.content.strip()
                            
                            if edit_choice == '1':
                                await user.send("📝 Enter the new task description:")
                                new_desc_msg = await bot.wait_for('message', timeout=120.0, check=check)
                                task['description'] = new_desc_msg.content.strip()
                                await user.send("✅ Task description updated!")
                            
                            elif edit_choice == '2':
                                await user.send("📝 Enter the new reward points:")
                                new_reward_msg = await bot.wait_for('message', timeout=60.0, check=check)
                                try:
                                    new_reward = int(new_reward_msg.content.strip())
                                    if new_reward > 0:
                                        task['reward_points'] = new_reward
                                        await user.send("✅ Reward points updated!")
                                    else:
                                        await user.send("❌ Reward points must be positive!")
                                except ValueError:
                                    await user.send("❌ Please enter a valid number!")
                            
                            elif edit_choice == '3':
                                await user.send("📝 Enter the new number of members:")
                                new_members_msg = await bot.wait_for('message', timeout=60.0, check=check)
                                try:
                                    new_members = int(new_members_msg.content.strip())
                                    if new_members > 0:
                                        task['max_members'] = new_members
                                        await user.send("✅ Number of members updated!")
                                    else:
                                        await user.send("❌ Number of members must be positive!")
                                except ValueError:
                                    await user.send("❌ Please enter a valid number!")
                            
                            else:
                                await user.send("❌ Invalid choice!")
                        else:
                            await user.send("❌ Invalid task number!")
                    except ValueError:
                        await user.send("❌ Please enter a valid number!")
                
                elif task_choice == '4':
                    # View current tasks
                    await user.send("📝 **Current tasks:**")
                    for i, task in enumerate(project['tasks'], 1):
                        if isinstance(task, dict):
                            await user.send(f"{i}. {task['description']} (Reward: {task['reward_points']} points, Members: {task['max_members']})")
                
                else:
                    await user.send("❌ Invalid choice!")
                
            elif choice == '3':
                await user.send("📝 Enter the new status (e.g., 'In Progress', 'Completed', 'On Hold'):")
                status_msg = await bot.wait_for('message', timeout=60.0, check=check)
                project['status'] = status_msg.content.strip()
                await user.send("✅ Project status updated!")
                
            else:
                await user.send("❌ Invalid choice!")
                return
                
        except asyncio.TimeoutError:
            await user.send("⏰ Timeout! Project editing cancelled.")
            return
        
        pm.save_data()
        await user.send("✅ Project updated successfully!")
        
    except Exception as e:
        await user.send(f"❌ Error editing project: {str(e)}")

async def delete_project_interactive(user, project_name):
    """Interactive project deletion process"""
    try:
        await user.send("⚠️ **Final Confirmation:** Type 'DELETE' to confirm project deletion:")
        
        def check(m):
            return m.author == user and m.channel.type == discord.ChannelType.private
        
        try:
            confirm_msg = await bot.wait_for('message', timeout=30.0, check=check)
            
            if confirm_msg.content.strip().upper() == 'DELETE':
                # Delete the project from data
                del pm.projects[project_name]
                pm.save_data()
                
                # Try to delete the forum thread
                forum_thread_deleted = await delete_forum_thread(project_name, user)
                
                # Send confirmation message
                embed = discord.Embed(
                    title="✅ Project Deleted Successfully!",
                    description=f"Project **{project_name}** has been permanently deleted.",
                    color=0x00ff00
                )
                embed.add_field(name="Project Data", value="✅ Removed from database", inline=True)
                
                if forum_thread_deleted:
                    embed.add_field(name="Forum Thread", value="✅ Deleted from forum", inline=True)
                else:
                    embed.add_field(name="Forum Thread", value="⚠️ Could not delete (may not exist)", inline=True)
                
                embed.add_field(name="Deleted by", value=user.name, inline=True)
                
                await user.send(embed=embed)
            else:
                await user.send("❌ Deletion cancelled.")
                
        except asyncio.TimeoutError:
            await user.send("⏰ Timeout! Deletion cancelled.")
            
    except Exception as e:
        await user.send(f"❌ Error deleting project: {str(e)}")

async def delete_forum_thread(project_name, user):
    """Deletes the forum thread for a project"""
    try:
        # Find the projects forum channel
        forum_channel = None
        configured_channel_name = pm.forum_channel_name
        
        for guild in bot.guilds:
            # First try to find the configured channel
            channel = discord.utils.get(guild.channels, name=configured_channel_name)
            if channel:
                # Check if it's actually a forum channel
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    forum_channel = channel
                    break
        
        if not forum_channel:
            print(f"Could not find forum channel '{configured_channel_name}' for project deletion: {project_name}")
            return False
        
        # Find the thread for this project
        thread = discord.utils.get(forum_channel.threads, name=f"Project: {project_name}")
        if not thread:
            print(f"Could not find forum thread for project deletion: {project_name}")
            return False
        
        # Check if bot has permission to delete the thread
        bot_member = forum_channel.guild.get_member(bot.user.id) if bot.user else None
        if not bot_member:
            print(f"Bot not found in server for project deletion: {project_name}")
            return False
        
        permissions = thread.permissions_for(bot_member)
        if not permissions.manage_threads:
            print(f"Bot doesn't have permission to delete thread for project: {project_name}")
            return False
        
        # Delete the thread
        await thread.delete()
        print(f"Successfully deleted forum thread for project: {project_name}")
        return True
        
    except Exception as e:
        print(f"Error deleting forum thread for project {project_name}: {str(e)}")
        return False

async def create_forum_post(project_name, description, tasks, user):
    """Creates a forum post for the new project"""
    try:
        # Find the projects forum channel
        forum_channel = None
        configured_channel_name = pm.forum_channel_name
        
        for guild in bot.guilds:
            # First try to find the configured channel
            channel = discord.utils.get(guild.channels, name=configured_channel_name)
            if channel:
                # Check if it's actually a forum channel
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    forum_channel = channel
                    break
                else:
                    # Channel exists but it's not a forum channel
                    embed = discord.Embed(
                        title="⚠️ Invalid Forum Channel",
                        description=f"Configured channel '{configured_channel_name}' is not a forum channel.",
                        color=0xff9900
                    )
                    embed.add_field(
                        name="Problem",
                        value=f"The configured channel '{configured_channel_name}' is a {channel.type.name} channel, not a forum channel.",
                        inline=False
                    )
                    embed.add_field(
                        name="How to fix",
                        value="Use `!project forums <forum_channel_name>` to configure a proper forum channel.",
                        inline=False
                    )
                    await user.send(embed=embed)
                    return
        
        if not forum_channel:
            embed = discord.Embed(
                title="⚠️ Forum Channel Not Found",
                description=f"Could not find forum channel: '{configured_channel_name}'",
                color=0xff9900
            )
            embed.add_field(
                name="How to fix",
                value="Use `!project forums <channel_name>` to configure the forum channel for project posts.",
                inline=False
            )
            embed.add_field(
                name="Available Forum Channels",
                value="Here are the available forum channels in this server:",
                inline=False
            )
            
            # List available forum channels
            forum_channels = []
            for guild in bot.guilds:
                for channel in guild.channels:
                    if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                        forum_channels.append(f"• {channel.name}")
            
            if forum_channels:
                channels_text = "\n".join(forum_channels[:10])  # Limit to 10 channels
                if len(forum_channels) > 10:
                    channels_text += f"\n... and {len(forum_channels) - 10} more"
                embed.add_field(name="Forums", value=channels_text, inline=False)
            else:
                embed.add_field(name="Forums", value="No forum channels found in this server", inline=False)
                embed.add_field(
                    name="How to create a forum channel",
                    value="1. Go to your server settings\n2. Click on 'Channels' in the left sidebar\n3. Click the '+' button to create a new channel\n4. Select 'Forum' as the channel type\n5. Name it (e.g., '📋・projects')\n6. Set appropriate permissions\n7. Click 'Create Channel'",
                    inline=False
                )
            
            embed.add_field(
                name="Note",
                value="Make sure the channel name is exactly correct, including any emojis or special characters.",
                inline=False
            )
            
            await user.send(embed=embed)
            return
        
        # Create the forum post
        embed = discord.Embed(
            title=f"📋 New Project: {project_name}",
            description=description,
            color=0x00ff00
        )
        
        # Add tasks to embed
        tasks_text = ""
        for i, task in enumerate(tasks, 1):
            tasks_text += f"{i}. **{task['description']}**\n   • Reward: {task['reward_points']} points\n   • Members needed: {task['max_members']}\n\n"
        
        embed.add_field(name="📝 Available Tasks", value=tasks_text[:1024], inline=False)
        embed.add_field(name="👤 Created by", value=user.name, inline=True)
        embed.add_field(name="📅 Created", value=datetime.now().strftime('%Y-%m-%d %H:%M'), inline=True)
        embed.add_field(
            name="🎯 Next Steps",
            value=f"Use `!project {project_name} assign` to assign yourself to tasks in this project!",
            inline=False
        )
        
        # Create the forum post
        thread = await forum_channel.create_thread(
            name=f"Project: {project_name}",
            content=embed.description,
            embed=embed
        )
        
        await user.send(f"✅ Forum post created successfully in the projects forum!")
        
    except Exception as e:
        embed = discord.Embed(
            title="⚠️ Forum Post Error",
            description="Project was created successfully, but there was an error creating the forum post.",
            color=0xff9900
        )
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.add_field(
            name="Next Steps",
            value="The project is still functional. You can manually create a forum post or contact an administrator.",
            inline=False
        )
        await user.send(embed=embed)

@bot.command(name='completed')
async def complete_task(ctx, *, args=None):
    """Marks a task as completed and rewards users"""
    if not args:
        await ctx.send("❌ Please specify project name! Usage: `!completed project <name>`")
        return
    
    # Parse the arguments to handle project names with spaces
    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Please specify project name! Usage: `!completed project <name>`")
        return
    
    # Check if first word is "project"
    if parts[0].lower() != 'project':
        await ctx.send("❌ Invalid command. Use `!completed project <name>` to mark a task as completed.")
        return
    
    # Extract project name from the original message
    original_message = ctx.message.content
    project_pos = original_message.lower().find(' project ')
    if project_pos == -1:
        await ctx.send("❌ Invalid format! Use: `!completed project <name>`")
        return
    
    # Extract everything after "project "
    project_name = original_message[project_pos + 9:].strip()
    
    if not project_name:
        await ctx.send("❌ Please specify a project name! Usage: `!completed project <name>`")
        return
    
    # Check if project exists
    if project_name not in pm.projects:
        embed = discord.Embed(
            title="❌ Project Not Found",
            description=f"Project '{project_name}' not found!",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Projects",
            value="Use `!projects` to see all available projects.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    project = pm.projects[project_name]
    
    # Check if project has the new task structure
    if not project.get('tasks') or not isinstance(project['tasks'], list):
        embed = discord.Embed(
            title="❌ Invalid Project Structure",
            description=f"Project '{project_name}' doesn't have predefined tasks.",
            color=0xff6b6b
        )
        embed.add_field(
            name="How to fix",
            value="Use `!new project` to create a new project with proper task structure.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Find tasks assigned to the user
    user_id = str(ctx.author.id)
    user_tasks = []
    
    for i, task in enumerate(project['tasks'], 1):
        if isinstance(task, dict) and not task.get('completed', False):
            if user_id in task.get('assigned_members', []):
                user_tasks.append((i, task))
    
    if not user_tasks:
        embed = discord.Embed(
            title="❌ No Assigned Tasks",
            description=f"You don't have any incomplete tasks assigned in project '{project_name}'.",
            color=0xff6b6b
        )
        embed.add_field(
            name="How to get tasks",
            value="Use `!project <name> assign <task>` to assign yourself to tasks in this project.",
            inline=False
        )
        
        # Show available tasks they can assign to
        available_tasks = []
        for i, task in enumerate(project['tasks'], 1):
            if isinstance(task, dict) and not task.get('completed', False):
                member_count = len(task.get('assigned_members', []))
                available_tasks.append(f"{i}. **{task['description']}** (Reward: {task['reward_points']} points, Members: {member_count}/{task['max_members']})")
        
        if available_tasks:
            embed.add_field(
                name="Available Tasks to Assign",
                value="\n".join(available_tasks[:5]) + ("\n..." if len(available_tasks) > 5 else ""),
                inline=False
            )
        
        await ctx.send(embed=embed)
        return
    
    # Show user's assigned tasks
    embed = discord.Embed(
        title=f"📋 Your Tasks in {project_name}",
        description="Select a task to mark as completed by typing its number, or type 'exit' to cancel:",
        color=0x0099ff
    )
    
    task_list = []
    for task_num, task in user_tasks:
        task_list.append(f"{task_num}. **{task['description']}** (Reward: {task['reward_points']} points)")
    
    embed.add_field(name="Your Assigned Tasks", value="\n".join(task_list), inline=False)
    embed.add_field(name="Instructions", value="Type the number of the task you want to complete, or 'exit' to cancel.", inline=False)
    
    await ctx.send(embed=embed)
    
    # Wait for user response
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        response = await bot.wait_for('message', timeout=60.0, check=check)
        choice = response.content.strip().lower()
        
        if choice == 'exit':
            await ctx.send("❌ Task completion cancelled.")
            return
        
        try:
            task_index = int(choice) - 1  # Convert to 0-based index
            if task_index < 0 or task_index >= len(project['tasks']):
                await ctx.send("❌ Invalid task number! Please try again.")
                return
            
            # Find the selected task
            selected_task = None
            for i, task in enumerate(project['tasks']):
                if isinstance(task, dict) and not task.get('completed', False):
                    if user_id in task.get('assigned_members', []):
                        if i == task_index:
                            selected_task = task
                            break
            
            if not selected_task:
                await ctx.send("❌ Invalid task selection! Please try again.")
                return
            
            # Mark task as completed
            selected_task['completed'] = True
            selected_task['completed_by'] = user_id
            selected_task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Reward all members who worked on the task
            assigned_members = selected_task.get('assigned_members', [])
            reward_per_member = selected_task['reward_points'] // len(assigned_members) if assigned_members else 0
            
            rewarded_users = []
            for member_id in assigned_members:
                if member_id not in pm.user_points:
                    pm.user_points[member_id] = 0
                pm.user_points[member_id] += reward_per_member
                rewarded_users.append(member_id)
            
            # Update project progress
            total_tasks = len(project['tasks'])
            completed_tasks = sum(1 for task in project['tasks'] if isinstance(task, dict) and task.get('completed', False))
            project['progress'] = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            
            # Check if all tasks are completed
            if completed_tasks == total_tasks:
                project['status'] = 'Completed'
            
            pm.save_data()
            
            # Create completion embed
            embed = discord.Embed(
                title="🎉 Task Completed!",
                description=f"Task **{selected_task['description']}** has been completed in project **{project_name}**!",
                color=0x00ff00
            )
            
            # Add member mentions
            member_mentions = []
            for member_id in assigned_members:
                try:
                    member = await bot.fetch_user(int(member_id))
                    member_mentions.append(member.mention)
                except:
                    member_mentions.append(f"<@{member_id}>")
            
            embed.add_field(name="Task", value=selected_task['description'], inline=False)
            embed.add_field(name="Completed by", value=ctx.author.mention, inline=True)
            embed.add_field(name="Team Members", value=", ".join(member_mentions), inline=True)
            embed.add_field(name="Reward per Member", value=f"{reward_per_member} points", inline=True)
            embed.add_field(name="Total Reward", value=f"{selected_task['reward_points']} points", inline=True)
            embed.add_field(name="Project Progress", value=f"{project['progress']}%", inline=True)
            
            if project['status'] == 'Completed':
                embed.add_field(name="🎊 Project Status", value="**COMPLETED!** All tasks finished!", inline=False)
            
            await ctx.send(embed=embed)
            
            # Update forum post
            await update_forum_post(project_name, project)
            
        except ValueError:
            await ctx.send("❌ Please enter a valid number or 'exit' to cancel.")
            return
            
    except asyncio.TimeoutError:
        await ctx.send("⏰ Timeout! Task completion cancelled.")
        return

async def update_forum_post(project_name, project):
    """Updates the forum post for a project"""
    try:
        # Find the projects forum channel
        forum_channel = None
        configured_channel_name = pm.forum_channel_name
        
        for guild in bot.guilds:
            # First try to find the configured channel
            channel = discord.utils.get(guild.channels, name=configured_channel_name)
            if channel:
                # Check if it's actually a forum channel
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    forum_channel = channel
                    break
        
        if not forum_channel:
            print(f"Could not find forum channel '{configured_channel_name}' for project: {project_name}")
            return
        
        # Find the thread for this project
        thread = discord.utils.get(forum_channel.threads, name=f"Project: {project_name}")
        if not thread:
            print(f"Could not find forum thread for project: {project_name}")
            return
        
        # Create updated embed
        embed = discord.Embed(
            title=f"📋 Project: {project_name}",
            description=project.get('description', 'No description available'),
            color=0x00ff00 if project['status'] == 'Completed' else 0x0099ff
        )
        
        # Add project info
        embed.add_field(name="Status", value=project['status'], inline=True)
        embed.add_field(name="Progress", value=f"{project['progress']}%", inline=True)
        embed.add_field(name="Created by", value=project.get('created_by', 'Unknown'), inline=True)
        
        # Add tasks with completion status
        tasks_text = ""
        for i, task in enumerate(project['tasks'], 1):
            if isinstance(task, dict):
                status_emoji = "✅" if task.get('completed', False) else "⏳"
                member_count = len(task.get('assigned_members', []))
                tasks_text += f"{i}. {status_emoji} **{task['description']}**\n   • Reward: {task['reward_points']} points\n   • Members: {member_count}/{task['max_members']}\n\n"
        
        if tasks_text:
            embed.add_field(name="📝 Tasks", value=tasks_text[:1024], inline=False)
        
        # Add project members
        if project.get('members'):
            members_text = ", ".join(project['members'])
            embed.add_field(name="👥 Team Members", value=members_text[:1024], inline=False)
        
        # Send update to thread
        await thread.send(embed=embed)
        
    except Exception as e:
        print(f"Error updating forum post for project {project_name}: {str(e)}")

@bot.command(name='forums')
async def forums_command(ctx, *, channel_name=None):
    """Configures the forum channel for project posts"""
    await configure_forum_channel(ctx, channel_name)

async def configure_forum_channel(ctx, channel_name):
    """Configures the forum channel for project posts"""
    # Check if user has required roles
    user_roles = [role.name for role in ctx.author.roles]
    if not pm.has_permission(user_roles, 'forum_config'):
        await ctx.send("❌ You don't have permission to configure forum channels. Contact an administrator to configure permissions.")
        return
    
    if not channel_name:
        # Show current configuration
        embed = discord.Embed(
            title="📋 Forum Channel Configuration",
            description="Current forum channel configuration:",
            color=0x0099ff
        )
        embed.add_field(name="Current Channel", value=pm.forum_channel_name, inline=True)
        embed.add_field(name="Configured by", value="System", inline=True)
        
        # Check if channel exists and is a forum channel
        channel_exists = False
        is_forum_channel = False
        for guild in bot.guilds:
            channel = discord.utils.get(guild.channels, name=pm.forum_channel_name)
            if channel:
                channel_exists = True
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    is_forum_channel = True
                break
        
        if channel_exists and is_forum_channel:
            status_emoji = "✅"
            status_text = "Forum Channel Found"
        elif channel_exists and not is_forum_channel:
            status_emoji = "⚠️"
            status_text = "Channel Found (Not Forum)"
        else:
            status_emoji = "❌"
            status_text = "Not Found"
        
        embed.add_field(name="Status", value=f"{status_emoji} {status_text}", inline=True)
        
        embed.add_field(
            name="How to change",
            value="Use `!project forums <channel name>` to set a new forum channel",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Validate channel name length
    if len(channel_name) > 100:
        await ctx.send("❌ Channel name is too long! Please use a shorter name (max 100 characters).")
        return
    
    # Check if the channel exists and is a forum channel
    channel_exists = False
    is_forum_channel = False
    found_channel = None
    
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel:
            channel_exists = True
            found_channel = channel
            if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                is_forum_channel = True
            break
    
    if not channel_exists:
        embed = discord.Embed(
            title="❌ Channel Not Found",
            description=f"Could not find a channel named '{channel_name}'",
            color=0xff6b6b
        )
        embed.add_field(
            name="Available Forum Channels",
            value="Here are the available forum channels in this server:",
            inline=False
        )
        
        # List available forum channels
        forum_channels = []
        for guild in bot.guilds:
            for channel in guild.channels:
                if hasattr(channel, 'type') and channel.type == discord.ChannelType.forum:
                    forum_channels.append(f"• {channel.name}")
        
        if forum_channels:
            channels_text = "\n".join(forum_channels[:10])  # Limit to 10 channels
            if len(forum_channels) > 10:
                channels_text += f"\n... and {len(forum_channels) - 10} more"
            embed.add_field(name="Forums", value=channels_text, inline=False)
        else:
            embed.add_field(name="Forums", value="No forum channels found in this server", inline=False)
            embed.add_field(
                name="How to create a forum channel",
                value="1. Go to your server settings\n2. Click on 'Channels' in the left sidebar\n3. Click the '+' button to create a new channel\n4. Select 'Forum' as the channel type\n5. Name it (e.g., '📋・projects')\n6. Set appropriate permissions\n7. Click 'Create Channel'",
                inline=False
            )
        
        embed.add_field(
            name="Note",
            value="Make sure the channel name is exactly correct, including any emojis or special characters.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    if not is_forum_channel:
        embed = discord.Embed(
            title="❌ Invalid Channel Type",
            description=f"Channel '{channel_name}' exists but is not a forum channel.",
            color=0xff6b6b
        )
        embed.add_field(
            name="Problem",
            value=f"The channel '{channel_name}' is a {found_channel.type.name if found_channel and hasattr(found_channel, 'type') else 'Unknown'} channel, not a forum channel.",
            inline=False
        )
        embed.add_field(
            name="How to fix",
            value="1. Create a new forum channel in your server\n2. Use `!project forums <forum_channel_name>` to configure it",
            inline=False
        )
        embed.add_field(
            name="Steps to create a forum channel",
            value="1. Go to your server settings\n2. Click on 'Channels' in the left sidebar\n3. Click the '+' button to create a new channel\n4. Select 'Forum' as the channel type\n5. Name it (e.g., '📋・projects')\n6. Set appropriate permissions\n7. Click 'Create Channel'",
            inline=False
        )
        embed.add_field(
            name="Note",
            value="Forum channels are required for project management. Regular text channels cannot be used for project posts.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Check if bot has required permissions in the forum channel
    if not found_channel:
        embed = discord.Embed(
            title="❌ Channel Error",
            description="Channel was found but is not accessible.",
            color=0xff6b6b
        )
        await ctx.send(embed=embed)
        return
    
    bot_member = found_channel.guild.get_member(bot.user.id) if bot.user else None
    if not bot_member:
        embed = discord.Embed(
            title="❌ Bot Not Found in Server",
            description="The bot is not a member of this server.",
            color=0xff6b6b
        )
        await ctx.send(embed=embed)
        return
    
    permissions = found_channel.permissions_for(bot_member)
    missing_permissions = []
    
    if not permissions.create_public_threads:
        missing_permissions.append("Create Public Threads")
    if not permissions.send_messages:
        missing_permissions.append("Send Messages")
    if not permissions.embed_links:
        missing_permissions.append("Embed Links")
    
    if missing_permissions:
        embed = discord.Embed(
            title="❌ Insufficient Bot Permissions",
            description=f"The bot doesn't have the required permissions in forum channel '{channel_name}'",
            color=0xff6b6b
        )
        embed.add_field(
            name="Missing Permissions",
            value="\n".join([f"• {perm}" for perm in missing_permissions]),
            inline=False
        )
        embed.add_field(
            name="How to fix",
            value="Ask an administrator to grant the bot these permissions in the forum channel:",
            inline=False
        )
        embed.add_field(
            name="Required Permissions",
            value="• Send Messages\n• Create Public Threads\n• Embed Links",
            inline=False
        )
        embed.add_field(
            name="Steps",
            value="1. Right-click the forum channel\n2. Select 'Edit Channel'\n3. Go to 'Permissions' tab\n4. Add the bot role\n5. Grant the required permissions\n6. Save changes",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Update the forum channel name
    old_channel = pm.forum_channel_name
    pm.forum_channel_name = channel_name
    pm.save_data()
    
    embed = discord.Embed(
        title="✅ Forum Channel Updated!",
        description="The forum channel for project posts has been updated successfully.",
        color=0x00ff00
    )
    embed.add_field(name="Previous Channel", value=old_channel, inline=True)
    embed.add_field(name="New Channel", value=channel_name, inline=True)
    embed.add_field(name="Updated by", value=ctx.author.mention, inline=True)
    embed.add_field(name="Channel Type", value="Forum Channel ✅", inline=True)
    embed.add_field(
        name="Next Steps",
        value="New projects will now be posted to this forum channel. Existing projects will continue to use their current forum threads.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='perm')
async def configure_permissions(ctx, action=None, *, role_name=None):
    """Configures role permissions for restricted commands"""
    # Check if user is server owner
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Only the server owner can configure permissions!")
        return
    
    if not action:
        await ctx.send("❌ Please specify an action! Usage: `!perm <action> <role>`\nActions: `add`, `remove`, `view`")
        return
    
    if not role_name or role_name.strip() == "":
        await ctx.send("❌ Please specify a role name! Usage: `!perm <action> <role_name>`")
        return
    
    action = action.lower().strip()
    role_name = role_name.strip()
    
    # Check if the role exists
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Role '{role_name}' not found!")
        return
    
    if action == 'view':
        # Show current permissions
        embed = discord.Embed(
            title="🔐 Permission Configuration",
            description=f"Current permissions for role: **{role_name}**",
            color=0x0099ff
        )
        
        # Show current permissions
        current_perms = []
        for perm_type, roles in pm.permissions.items():
            status = "✅" if role_name in roles else "❌"
            perm_name = {
                'project_management': 'Project Management (new/edit/delete)',
                'forum_config': 'Forum Configuration',
                'shop_management': 'Shop Management',
                'permission_management': 'Permission Management'
            }.get(perm_type, perm_type)
            current_perms.append(f"{status} {perm_name}")
        
        embed.add_field(name="Current Permissions", value="\n".join(current_perms), inline=False)
        embed.add_field(
            name="How to configure",
            value="Use `!perm add <role>` to grant all permissions\nUse `!perm remove <role>` to revoke all permissions",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    elif action == 'add':
        # Grant all permissions (except permission_management which is owner only)
        permissions_to_grant = ['project_management', 'forum_config', 'shop_management']
        changes_made = []
        
        for perm_key in permissions_to_grant:
            if role_name not in pm.permissions[perm_key]:
                pm.permissions[perm_key].append(role_name)
                changes_made.append(f"✅ Granted {perm_key.replace('_', ' ')} permission")
        
        if not changes_made:
            embed = discord.Embed(
                title="ℹ️ No Changes Needed",
                description=f"Role **{role_name}** already has all available permissions.",
                color=0x0099ff
            )
        else:
            pm.save_data()
            embed = discord.Embed(
                title="✅ Permissions Granted!",
                description=f"All permissions granted to role: **{role_name}**",
                color=0x00ff00
            )
            for change in changes_made:
                embed.add_field(name="Permission", value=change, inline=True)
        
        embed.add_field(name="Updated by", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        return
    
    elif action == 'remove':
        # Remove all permissions
        permissions_to_remove = ['project_management', 'forum_config', 'shop_management']
        changes_made = []
        
        for perm_key in permissions_to_remove:
            if role_name in pm.permissions[perm_key]:
                pm.permissions[perm_key].remove(role_name)
                changes_made.append(f"❌ Removed {perm_key.replace('_', ' ')} permission")
        
        if not changes_made:
            embed = discord.Embed(
                title="ℹ️ No Changes Needed",
                description=f"Role **{role_name}** doesn't have any permissions to remove.",
                color=0x0099ff
            )
        else:
            pm.save_data()
            embed = discord.Embed(
                title="✅ Permissions Removed!",
                description=f"All permissions removed from role: **{role_name}**",
                color=0xff6b6b
            )
            for change in changes_made:
                embed.add_field(name="Permission", value=change, inline=True)
        
        embed.add_field(name="Updated by", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        return
    
    else:
        await ctx.send("❌ Invalid action! Available actions: `add`, `remove`, `view`")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Use `!commands` to see command usage.")
    elif isinstance(error, commands.CommandNotFound):
        # Provide command suggestions
        command_name = ctx.message.content.split()[0][1:]  # Remove the ! prefix
        suggestions = get_command_suggestions(command_name)
        
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"Command `{ctx.message.content}` not found.",
            color=0xff6b6b
        )
        
        if suggestions:
            embed.add_field(
                name="💡 Did you mean?",
                value="\n".join([f"• `!{suggestion}`" for suggestion in suggestions]),
                inline=False
            )
        
        embed.add_field(
            name="📚 Help",
            value="Use `!commands` to see all available commands.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided. Use `!commands` to see command usage.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

def get_command_suggestions(partial_command):
    """Returns command suggestions based on partial input"""
    all_commands = [
        'commands', 'roles', 'role', 'nickname', 'projects', 'project', 
        'rewards', 'shop', 'new', 'edit', 'delete', 'completed', 'forums', 'perm'
    ]
    
    suggestions = []
    partial_lower = partial_command.lower()
    
    for cmd in all_commands:
        if partial_lower in cmd or cmd.startswith(partial_lower):
            suggestions.append(cmd)
    
    # Also check for common misspellings
    common_misspellings = {
        'projct': 'project',
        'projet': 'project',
        'comand': 'commands',
        'comands': 'commands',
        'rol': 'role',
        'roles': 'role',
        'rewads': 'rewards',
        'reard': 'rewards',
        'shp': 'shop',
        'shopp': 'shop'
    }
    
    if partial_lower in common_misspellings:
        suggestions.append(common_misspellings[partial_lower])
    
    return list(set(suggestions))[:5]  # Return up to 5 unique suggestions

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
