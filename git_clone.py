#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# 2020-07-28 GitLab Group代码拉取脚本
import os, requests, re, json, subprocess

git_addr = 'https://gitlab.xxx.com'
git_group = 'xl'
git_branches = 'master'
git_user = 'xxx'
git_pass = 'xxxxxx'
local_addr = 'd:\\'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'


def get_auth():
    # 发送GET请求,拿到未授权的cookie，拿到服务器返回的authenticity_token
    request_get = requests.get(git_addr + '/users/sign_in/', headers={'User-Agent': user_agent}, )
    authenticity_token = re.findall(r'name="authenticity_token".*?value="(.*?)"', request_get.text, re.S)[0]
    unauth_cookies = request_get.cookies.get_dict()
    # 带着未授权的cookie，authenticity_token，账号密码发送POST请求，拿到输入正确用户名和密码后的授权的cookie。
    request_post = requests.post(git_addr + '/users/sign_in', data={
        'utf8': '✓',
        'authenticity_token': authenticity_token,
        'user[login]': git_user,
        'user[password]': git_pass,
        'user[remember_me]': 1
    },
                                 headers={'User-Agent': user_agent},
                                 cookies=unauth_cookies
                                 )
    auth_cookies = request_post.cookies.get_dict()
    return auth_cookies


def main():
    # 在本地新建代码保存路径
    if not os.path.exists(local_addr + '\\' + git_group):
        os.makedirs(local_addr + '\\' + git_group)
    cookies = get_auth()
    # 通过git的api接口获取group下所有项目信息
    print (git_addr + "/api/v4/groups/" + git_group)
    response = requests.get(git_addr + "/api/v4/groups/" + git_group, cookies=cookies)
    # 循环拉取group下所有项目
    for i in json.loads(response.text)['projects']:
        save_path = local_addr + '\\' + git_group + '\\' + i['name']
        print("Pull Project：", i['name'] + "", end="")
        status, output = subprocess.getstatusoutput(
            'git.exe clone --progress --branch ' + git_branches + ' --origin ' + git_branches + ' -v ' + i[
                'http_url_to_repo'] + ' ' + save_path)
        print("   OK!!!") if status == 0 else ("   Failed!!!")


if __name__ == '__main__':
    main()