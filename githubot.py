from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
import asyncio
import aiohttp
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain ,At
from graia.application.event.messages import Group
from graia.application.event.messages import Member


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

async def getRepositoryInfo(keyword: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.github.com/search/repositories?q={keyword}',
                          headers={'accept': 'application/vnd.github.v3+json'}) as response:
            search = response.json()
    if search.get('total_count') != 0:
        repo_data = search.get('items')[0]
        full_name = repo_data.get('full_name')
        owner = repo_data.get('owner').get('login')
        description = repo_data.get('description')
        watch = repo_data.get('watchers')
        star = repo_data.get('stargazers_count')
        fork = repo_data.get('forks_count')
        language = repo_data.get('language')
        license = 'None'
        try:
            license = repo_data.get('license').get('spdx_id')
        except:
            pass
        last_pushed = repo_data.get('pushed_at')
        jump = repo_data.get('html_url')
        text=f'{full_name}:\nOwner:{owner}\nDescription:{description}\nWatch/Star/Fork:{watch}/{star}/{fork}\nLanguage:{language}\nLicense:{license}\nLast pushed:{last_pushed}\nJump:{jump}'
        return text
    else:
        return '无此存储库'

async def getIssueInfo(repository: str, issue_number: int) -> str:
    #@0x7FFFFF
    #Issue: #941
    #Title: MCL环境下登录缓慢或者无法登陆
    #Jump: https://github.com/mamoe/mirai/issues/941
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.github.com/repos/{repository}/issues/{issue_number}',
                          headers={'accept': 'application/vnd.github.v3.text+json', }) as response:
            status = response.status
            response: dict = await response.json()
    if status == 200:
        title = response.get('title')
        jump = response.get('html_url')
        return f"Issue: #{str(issue_number)}\nTitle: {title}\nJump: {jump}"
    else:
        return '无此Issue'

@bcc.receiver("GroupMessage")
async def group_message_handler(app: GraiaMiraiApplication, msgchain: MessageChain, group: Group, member: Member):
    if msgchain.asDisplay().startswith("#G"):
        await app.sendGroupMessage(group, MessageChain.create(
            [At(member.id), Plain(await getRepositoryInfo(msgchain.asDisplay().replace('#G','').lstrip().rstrip()))]))
    elif msgchain.asDisplay().startswith("#I"):
        repository = msgchain.asDisplay().replace('#I', '').lstrip().rstrip().split(' ')[0]
        issue_number = int(msgchain.asDisplay().replace('#I', '').lstrip().rstrip().split(' ')[1].replace('#',''))
        await app.sendGroupMessage(group, MessageChain.create(
            [At(member.id), Plain(await getIssueInfo(repository,issue_number))]))

if __name__ == "__main__":
    app.launch_blocking()
