ls
If you are just cloning the repo for the first time, since it has git submodules

```bash
git clone --recurse-submodules https://github.com/calvinw/BusMgmtDoltDatabase.git
```

Or if you already cloned the regular way you can do this:

```bash
git clone https://github.com/calvinw/BusMgmtDoltDatabase.git
cd BusMgmtDoltDatabase
git submodule update --init --recursive
```


[BusMgmtDoltDatabaseDocumentation.md](https://calvinw.github.io/BusMgmtDoltDatabase/docs/BusMgmtDoltDatabaseDocumentation.md)

[RestApiBusMgmtDoltDatabase.md](https://calvinw.github.io/BusMgmtDoltDatabase/docs/RestApiBusMgmtDoltDatabase.md)
