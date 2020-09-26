import asyncio
import jinja2


async def myfilter(instr):
    import datetime
    print("kaishi", datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
    await asyncio.sleep(1)
    print("jieshu", datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
    return f'Hello {instr}'


async def main():

    env = jinja2.Environment(enable_async=True)
    env.filters['myfilter'] = myfilter

    tmpl = env.from_string('{{"test1"|myfilter}}\n{{x|myfilter}}')

    text = await tmpl.render_async(x='test2')
    print(text)


if __name__ == '__main__':
    asyncio.run(main())
