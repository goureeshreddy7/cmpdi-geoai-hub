with open('c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/frontend/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print('#page-query found:', '<div id="page-query"' in c)
print('#user-chat-messages found:', 'id="user-chat-messages"' in c)
print('#nav-query found:', 'id="nav-query"' in c)
print('#geoai-floating-assistant-root found:', 'id="geoai-floating-assistant-root"' in c)
print('#geoai-floating-chat-window found:', 'id="geoai-floating-chat-window"' in c)
print('Total lines in index.html:', len(c.splitlines()))
