from config import save_config, load_config, select_folder
from converter import process_files
from watcher import watch_folder

config = load_config()

if config is not None:
    input_dir, output_dir = config

    print('IN:', input_dir)
    print('OUT:', output_dir)

    folders_exist = input_dir.exists() and output_dir.exists()

    if not input_dir.exists():
        print('Папка IN не найдена')

        input_base_dir = select_folder()

        if input_base_dir is not None:
            input_dir = input_base_dir / 'in'
            input_dir.mkdir(exist_ok=True)

            print('Новая IN:', input_dir)

            save_config(input_dir, output_dir)

    if not output_dir.exists():
        print('Папка OUT не найдена')

        output_base_dir = select_folder()

        if output_base_dir is not None:
            output_dir = output_base_dir / 'out'
            output_dir.mkdir(exist_ok=True)

            print('Новая OUT:', output_dir)

            save_config(input_dir, output_dir)

    if folders_exist:
        print('Папки найдены')

else:
    input_base_dir = select_folder()

    # назначаем и создаем папки IN/OUT
    if input_base_dir is not None:
        input_dir = input_base_dir / 'in'  # создаем папку in
        input_dir.mkdir(exist_ok=True)

        print('IN:', input_dir)

        output_base_dir = select_folder()

        if output_base_dir is not None:
            output_dir = output_base_dir / 'out'
            output_dir.mkdir(exist_ok=True)

            print('OUT:', output_dir)

            save_config(input_dir, output_dir)
        else:
            print('Место для OUT не выбрано')

    else:
        print('Место для IN не выбрано')

if input_dir.exists() and output_dir.exists():
    process_files(input_dir, output_dir)
    watch_folder(input_dir)
