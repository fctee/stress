
class Config:
    # 云手机ip集
    IPS = [
        "172.31.221.244",
        "172.31.99.117",
        "172.31.106.110",
        "172.31.32.29",
        "172.31.118.17",
        "172.31.20.83",
        "172.31.248.224",
        "172.31.89.37",
        "172.31.47.57",
        "172.31.254.109",
        "172.31.174.246",
        "172.31.166.16",
        "172.31.114.112",
        "172.31.131.231",
        "172.31.54.42",
        "172.31.31.207",
        "172.31.67.210",
        "172.31.12.239",
        "172.31.112.127",
        "172.31.57.9",
        "172.31.78.233",
        "172.31.151.184",
        "172.31.34.64",
        "172.31.75.200",
        "172.31.137.147",
        "172.31.127.193",
        "172.31.198.169",
        "172.31.231.141",
        "172.31.3.13",
        "172.31.140.135",
        "172.31.235.204",
        "172.31.7.119",
        "172.31.233.211",
        "172.31.14.221",
        "172.31.26.91",
        "172.31.96.162",
        "172.31.162.191",
        "172.31.240.88",
        "172.31.23.238",
        "172.31.132.166",
        "172.31.38.53",
        "172.31.44.179",
        "172.31.32.19",
        "172.31.238.26",
        "172.31.229.217",
        "172.31.218.139",
        "172.31.233.197",
        "172.31.31.208",
        "172.31.103.18",
        "172.31.36.160"
    ]
    # 云手机port集, 从4555到4673的奇数
    PORTS = [u"%s" % i for i in list(range(4555, 4674)) if i % 2 != 0]
    HTML_TPL = "log_template.html"