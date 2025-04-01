
### Injection POC
- ``amdxx64.dll`` & ``nviapi64.dll`` Are both whitelisted DLL's, that roblox allow's to be loaded therfore you can use ``SetWindowsHookExA``
-  Another method of injection is ``Cert Spoofing``, Spoofing the Cert to any Whitelisted DLL's Cert, Require's a REG edit though to allow fake cert's https://github.com/secret-blox/secret-blox-sign
-  Rename any DLL to ``amdxx64.dll`` or ``nviapi64.dll`` and in boblox.py change the ``DLL_PATH`` & ``DLL_CALLBACK``
-  ``Python12.9`` must run env as Admin for ``OpenProcess``

Dll must have an Hook Export ``Boblox`` Callback can be called anything
```c++
extern "C" __declspec(dllexport) LRESULT Boblox(int Code, WPARAM WParam, LPARAM LParam) {
    return CallNextHookEx(nullptr, Code, WParam, LParam);
}
```



# UwU
![image](https://github.com/user-attachments/assets/771dcb45-8a55-4e26-9814-80bb4d815a85)
