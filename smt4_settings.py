from settings import UserFilePath, Group

settings_key = "smt4"


class SMT4RomFile(UserFilePath):
    """File name of your decrypted North American Shin Megami Tensei IV ROM"""
    description = "Shin Megami Tensei IV ROM File"

    def browse(self, filetypes=None, **kwargs):
        filetypes = [("3ds ROM File", [".3ds"])]
        return super().browse(filetypes=filetypes, **kwargs)

    @classmethod
    def validate(cls, path: str) -> None:
        pass


class AzaharPath(UserFilePath):
    """Path to your Azahar emulator"""
    description = "Path to Azahar emulator"
    is_exe = True


class SMT4Settings(Group):
    rom_file: SMT4RomFile = SMT4RomFile("Shin Megami Tensei IV (USA).3ds")
    azahar_path: AzaharPath = AzaharPath("")
