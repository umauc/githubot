from graia.application import group
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.event.messages import GroupMessage
import asyncio
import requests
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain ,At
from graia.application.event.messages import Group
from graia.application.event.messages import Member
from requests.api import head

# 请根据需要配置代理
#proxies = {
#    'http': 'socks5://127.0.0.1:1080',
#    'https': 'socks5://127.0.0.1:1080'
#}

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session( #填写下面的内容
        host="", # 填入 httpapi 服务运行的地址
        authKey="", # 填入 authKey
        account=, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

@bcc.receiver("GroupMessage")
async def githubot(app: GraiaMiraiApplication, member: Member, messageChain: MessageChain, gm:GroupMessage , g: Group):
    if messageChain.asDisplay().find('#G') == 0:
        keyword = messageChain.asDisplay().replace('#G','').replace(' ','')
        try:
            search = requests.get(f'https://api.github.com/search/repositories?q={keyword}',headers={'accept': 'application/vnd.github.v3+json'}).json() # ,proxies=proxies
            if search.get('total_count') != 0:
                repo_data = search.get('items')[0]
                full_name = repo_data.get('full_name')
                owner = repo_data.get('owner').get('login')
                description = repo_data.get('description')
                watch = repo_data.get('watchers')
                star = repo_data.get('stargazers_count')
                fork = repo_data.get('forks_count')
                language = repo_data.get('language')
                open_issues = repo_data.get('open_issues')
                try:
                    license = repo_data.get('license').get('spdx_id')
                except:
                    license = 'None'
                last_pushed = repo_data.get('pushed_at')
                jump = repo_data.get('html_url') 
                mc = messageChain.create([At(target=member.id), Plain(text=f'{full_name}:\nOwner:{owner}\nDescription:{description}\nWatch/Star/Fork:{watch}/{star}/{fork}\nLanguage:{language}\nLicense:{license}\nLast pushed:{last_pushed}\nJump:{jump}')]).asSendable()
                await app.sendGroupMessage(g,mc)
        except:
            await app.sendGroupMessage(g,messageChain.create([At(target=member.id),Plain(text='无此存储库')]))

app.launch_blocking()
