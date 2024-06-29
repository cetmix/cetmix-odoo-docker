# Odoo Images for Cetmix Tower

## What is this?

These are Odoo images that are designed to be used with [Cetmix Tower](https://cetmix.com/tower). 
To learn more about Tower check the [Official website](https://cetmix.com/tower) of the project.

## Why not to use existing images?

There are many Odoo Docker images out there. Most well know and widely used are:

- [Odoo official image](https://github.com/odoo/docker) by Odoo
- [OCA CI image](https://github.com/OCA/oca-ci) by OCA
- [Doobda](https://github.com/Tecnativa/doodba) by Tecnativa
- [odoo-bedroc](https://github.com/acsone/odoo-bedrock) by Acsone
- [docker-odoo-project](https://github.com/camptocamp/docker-odoo-project/tree/master) by Camptocamp
- ..some others we forgot to mention (sorry)

Those images have a lot of cool features and power tools inside.
However [Cetmix Tower](https://cetmix.com/tower) already has all the tools.
So our images have only the features that are used by [Cetmix Tower](https://cetmix.com/tower) itself.

## Configuration

All configuration is done directly in the [Cetmix Tower](https://cetmix.com/tower). Use Tower variables to provide build arguments values.

Available build arguments:

- `ODOO_VERSION` Used for building requirements. Each Dockerfile already has default value set
- `DOCKER_ODOO_UID` User ID of `odoo` user. Default value `9999`  
- `DOCKER_ODOO_GID` Group ID of `odoo` user. Default value `9999`
- `POSTGRES_VERSION` Postgres version. Default is 14
- `TARGETARCH` Architecture to build image for. Will be detected automatically, specify custom value if needed. Eg `amd64` or `arm64` 
- `ODOO_HEAD` HEAD of Odoo git branch. Allows to checkout Odoo source code at custom HEAD. Default value == `ODOO_VERSION`
- `ODOO_ORG_REPO` Github repository with Odoo source code. You can use a custom one if needed. Default value is Odoo official repo: `odoo/odoo`
- `EXTRA_ADDONS_RELEASE` this is a technical argument used to prevent caching of the extra addons installation layers. Use [Cetmix Tower](https://cetmix.com/tower) {{ tower.tools.now }} system variable as a value to prevent cache usage for all commands after this argument.
- `DB_MANAGER_PASSWORD` Odoo database manager password. Default is `suchMuchPassword`



## Usage

Files for each Odoo version are located in the corresponding directories. Although [Cetmix Tower](https://cetmix.com/tower) uses its own file management system you can build your own image using provided files.
Use `addons.yml` file to add custom modules. Check [Git Aggregator](https://github.com/acsone/git-aggregator) documentation for details.
There is also a simple `docker-compose.yml` file which is meant for fast and easy testing.

**NB** Default Odoo database manager password is `suchMuchPassword`. You can provide you