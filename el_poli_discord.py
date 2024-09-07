import discord
from discord.ext import commands
from discord import Intents

# Función para cargar los códigos desde un archivo .txt
def load_codes(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f'Error: archivo {filename} no encontrado.')
        return []
    except Exception as e:
        print(f'Error al cargar el archivo: {e}')
        return []

# Función para guardar los códigos actualizados en el archivo .txt
def save_codes(filename, codes):
    try:
        with open(filename, 'w') as file:
            for code in codes:
                file.write(f'{code}\n')
        print(f'Lista de códigos actualizada y guardada en {filename}')
    except Exception as e:
        print(f'Error al guardar el archivo: {e}')

# Configurar intents
intents = Intents.all()
intents.members = True  # Permite que el bot reciba eventos relacionados con miembros

# Archivo que contiene los códigos permitidos
CODES_FILE = 'matriculas_inscritas.txt'  # Modificar la ruta según sea necesario

# Cargar los códigos al iniciar
valid_codes = load_codes(CODES_FILE)

# Bot prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento para cuando el bot esté listo
@bot.event
async def on_ready():
    print(f'{bot.user} está listo y conectado!')
    print(f'Numeros de control cargados: {valid_codes}')  # Depuración

# Verifica si el autor tiene el rol de Organizador o permisos de administrador
def is_organizer_or_admin(ctx):
    role_name = "Organizador"
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    return ctx.author.guild_permissions.administrator or (role in ctx.author.roles)

# Comando para ingresar un código
@bot.command()
async def ingresar(ctx, code: str):
    try:
        print(f'Lista de numeros de control: {valid_codes}')  # Depuración
        # Verifica si el código es válido
        if code in valid_codes:
            # Rol a asignar (debe coincidir con el nombre del rol en tu servidor)
            role = discord.utils.get(ctx.guild.roles, name="Participante")
            
            # Verifica si el rol existe
            if role:
                await ctx.author.add_roles(role)
                valid_codes.remove(code)  # Elimina el código de la lista
                try:
                    save_codes(CODES_FILE, valid_codes)  # Guarda la lista actualizada
                except Exception as e:
                    print(f'Error al guardar la lista de códigos: {e}')
                await ctx.send(f'¡Felicidades {ctx.author.mention}, has recibido el rol {role.name}, disfruta tu estancia!')
            else:
                await ctx.send('El rol no existe en este servidor.')
        else:
            await ctx.send('Error: Número de control inválido o erróneo, por favor inténtalo de nuevo.')
    except discord.DiscordException as e:
        await ctx.send(f'Error al intentar asignar el rol: {e}')
    except Exception as e:
        await ctx.send(f'Ocurrió un error inesperado: {e}')

# Comando para agregar varios códigos
@bot.command()
@commands.check(is_organizer_or_admin)  # Verifica si el usuario tiene el rol de Organizador o permisos de administrador
async def agregar(ctx, *codes):
    try:
        # `codes` es una tupla de argumentos, por lo que la transformamos en una lista
        codes = [code.strip() for code in ' '.join(codes).split(',') if code.strip()]
        new_codes = [code for code in codes if code not in valid_codes]
        
        if new_codes:
            valid_codes.extend(new_codes)
            try:
                save_codes(CODES_FILE, valid_codes)
            except Exception as e:
                print(f'Error al guardar la lista de códigos: {e}')
                await ctx.send(f'Ocurrió un error al intentar guardar los códigos. Por favor, revisa los permisos del archivo. Usuario: {ctx.author.name}')
                return
            await ctx.send(f'Códigos {", ".join(new_codes)} agregados correctamente.')
        else:
            await ctx.send('Todos los códigos ya existen en la lista.')
    except Exception as e:
        await ctx.send(f'Ocurrió un error inesperado al agregar códigos. Usuario: {ctx.author.name}. Error: {e}')

# Comando para ver todos los códigos
@bot.command()
@commands.check(is_organizer_or_admin)  # Verifica si el usuario tiene el rol de Organizador o permisos de administrador
async def ver(ctx):
    try:
        if valid_codes:
            codes_list = '\n'.join(valid_codes)
            await ctx.send(f'Numeros de control registrados:\n{codes_list}')
        else:
            await ctx.send('No hay códigos registrados.')
    except commands.CheckFailure as e:
        print(f'Error: Usuario {ctx.author.name} intentó usar el comando sin permisos necesarios. Error: {e}')
        await ctx.send(f'No tienes permisos suficientes para usar el comando `{ctx.command}`.')
    except Exception as e:
        print(f'Ocurrió un error inesperado al mostrar los numeros de control. Usuario: {ctx.author.name}. Error: {e}')
        await ctx.send(f'Ocurrió un error inesperado al mostrar los numeros de control. Por favor, revisa el log para más detalles.')

# Comando para eliminar un código
@bot.command()
@commands.check(is_organizer_or_admin)  # Verifica si el usuario tiene el rol de Organizador o permisos de administrador
async def eliminar(ctx, code: str):
    try:
        if code in valid_codes:
            valid_codes.remove(code)
            try:
                save_codes(CODES_FILE, valid_codes)
            except Exception as e:
                print(f'Error al guardar la lista de códigos: {e}')
                await ctx.send(f'Ocurrió un error al intentar guardar los códigos después de la eliminación. Por favor, revisa los permisos del archivo. Usuario: {ctx.author.name}')
                return
            await ctx.send(f'Numero de control {code} eliminado correctamente.')
        else:
            await ctx.send(f'El numero de control {code} no se encuentra en la lista de numeros de control.')
    except commands.CheckFailure as e:
        print(f'Error: Usuario {ctx.author.name} intentó usar el comando sin permisos necesarios. Error: {e}')
        await ctx.send(f'No tienes permisos suficientes para usar el comando `{ctx.command}`.')
    except Exception as e:
        print(f'Ocurrió un error inesperado al eliminar el numero de control. Usuario: {ctx.author.name}. Error: {e}')
        await ctx.send(f'Ocurrió un error inesperado al eliminar el código. Por favor, revisa el log para más detalles.')

# Iniciar el bot con el token
try:
    bot.run('Aqui va el token')  # Reemplaza con tu token real
except discord.LoginFailure:
    print('Error: El token de autenticación es inválido.')
except Exception as e:
    print(f'Ocurrió un error al iniciar el bot: {e}')
