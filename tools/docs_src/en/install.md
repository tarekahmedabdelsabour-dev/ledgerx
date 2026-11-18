> This page is for the system administrator.

## Updating

```
cd <bench-folder>/apps/<app-name>
git pull origin main
cd <bench-folder>
bench --site mysite.localhost migrate
bench --site mysite.localhost clear-cache
```

Then restart the services and refresh the browser by pressing `Ctrl + Shift + R`.

## Installing a new module

1. Copy the app to the apps folder.
2. Add it to the apps list and install it with the Python package.
3. Install it on the site, then run the migration and clear the cache.
4. Do a full restart.

> ! If you add the app to the list without copying and installing it, the server will not work. Verify that all the steps are complete.

## Backup

Run `bench --site mysite.localhost backup --with-files` regularly and keep the copies off the server.

## First steps when there are problems

- Open the **Error Log** from the system and copy the error text.
- Try clearing the cache and restarting.
- Check that all modules are installed on the site.
