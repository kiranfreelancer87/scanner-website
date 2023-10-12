#import asyncio, asyncssh, sys

#async def run_client(user,passwd,remoteip) -> None:
 #    async with asyncssh.connect(remoteip, username=user,password=passwd,known_hosts=None) as conn:
  #      #await conn.run('tail -r', input='1\n2\n3\n', stdout='/tmp/stdout')
   #     await conn.run("ls /home/app/", stdout='/tmp/stdout.txt')
    #    #await conn.run("show route 10.91.127.11", stdout='/tmp/stdout')
#try:
 #   # asyncio.get_event_loop().run_until_complete(run_client('root','asdf&8Jkl'))
  #  asyncio.run(run_client("root","asdf&8Jkl",'143.244.131.8'))
#except (OSError, asyncssh.Error) as exc:
 #   sys.exit('SSH connection failed: ' + str(exc))
