#!/usr/bin/python
# -_- encoding: utf8 -_-

import sys
sys.path.append('./test')
from http_utils import *

# =============
#
print('[+] Parse query args common test')

preset_method_location = BASE_URL + '/rest_api_parse_query_args'
args = {'arg1': 1, 'arg2': 2}
result = get_success(preset_method_location, args, {})
assert_query_args(result, args)

for i in range(1, 10):
    args['arg' + str(i)] = 'some_string_plus_' + str(i)
result = get_success(preset_method_location, args, {})
assert_query_args(result, args)

# =============
#
print('[+] Proto and method in result set')
result = get_success(preset_method_location, args, {})
result = result[0]
assert(result['proto'] == 'HTTP/1.1'), 'expected HTTP/1.1'
assert(result['method'] == 'GET'), 'expected GET, got'

# ============
#
print('[+] Parse query args overflow test')
for i in range(1, 100):
    args['arg' + str(i)] = 'some_string_plus_' + str(i)
(code, msg) = get_fail(preset_method_location, args, {})
assert(code == 414), 'expected http code 414'


# ============
#
print('[+] issue 44 (lua error from Tarantool)')

for suf in [ 'issue_44', 'issue_44_not_pure', 'issue_44_skip']:
  preset_method_location = BASE_URL + '/' + suf
  (code, msg) = get_fail(preset_method_location, {}, {})
  assert_if_not_error(msg, -32800)

# ============
#
print('[+] issue 43 (REST restriction)')

preset_method_location = BASE_URL + '/issue_43'
(code, msg) = get_fail(preset_method_location, {}, {})
assert(code == 405), "expected 405, got " + str(code)

preset_method_location = BASE_URL + '/issue_43'
result = post_success(preset_method_location, {
    'method':'echo_2', 'params':[[1,2,3], [4]], 'id': 1}, {})
assert (result == [1,2,3]), 'expected [1,2,3]'

preset_method_location =  BASE_URL + '/echo_1/issue_43_post_and_get'
result = post_success(preset_method_location, {
    'method':'echo_2', 'params':[[1,2,3],[4]], 'id': 1}, {})
assert (result == [1,2,3]), 'expected [1,2,3]'

preset_method_location = BASE_URL + '/echo_1/issue_43_post_and_get'

result = post_success(preset_method_location, {
    'params':[[1,2,3],[4]], 'id': 1}, {})
assert (result == [1,2,3]), 'expected [1,2,3]'

result = get_success(preset_method_location, {
  'params':[[1,2,3],[4]], 'id': 1}, {})

(code, msg) = put_fail(preset_method_location, {}, {})
assert(code == 405), 'expected 405, got ' + str(code)

# ===========
#
print('[+] UTF8')

data = """{"method": "echo_1", "id": 0, "params":[{"ключ 1":"значение"}]}"""
preset_method_location = BASE_URL + '/tnt'
rc, resp = request_raw(preset_method_location, data, {})
params = json.loads(data)['params']
assert(rc == 200), 'expected 200, got ' + str(rc)
assert(params == resp['result'][0]), 'not equal'

# ===========
#
print('[+] Long arrays of array of integers')

data = []
for i in range(1, 10):
    data.append([])
    for j in range(1, 10):
        data[i-1].append(100000000)

preset_method_location = BASE_URL + '/tnt'
result = post_success(preset_method_location, {
    'method':'echo_2', 'params':[{'array':data}], 'id': 1}, {})
assert(data == result[0]['array']), 'not equal'

#===========
#
print('[+] issue #52, the escaped characters')

preset_method_location = BASE_URL + '/tnt'
data = {
  "uid": 79031234567,
  "date": 201607251753,
  "text": "\"201607251753\"",
  "key - \n": "\t - value",
  "\"key\"\t": "\t\n - value"
}

result = post_success(preset_method_location, {
    'method':'echo_2', 'params':[data], 'id': 1}, {})
assert(data == result[0]), 'not equal'

#===========
#
print('[+] Empty string')
preset_method_location = BASE_URL + '/tnt'
post_success(preset_method_location, {
    'method':'four_empty_strings', 'params':[], 'id': 1}, {})
