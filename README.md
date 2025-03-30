# WE Usage

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Python script that monitors your TE Data (Egypt) ADSL usage in stdout. 
This allows porting to `Polybar`, `Conky`, etc.


## Add your credentials in this format:

```json
{
    "username": "FBB693779669",
    "password": "your_password"
}

```

## Usage

Compact use

```bash
./we_usage.py
```

Simple use (optimized for porting)

```bash
./we_usage.py --simple
```

## Polybar Integration

Add to your Polybar config (~/.config/polybar/config):

```ini
[module/te-usage]
type = custom/script
exec = /path/to/te_usage_monitor.py --simple
interval = 3600  # Update every hour
format = <label>
label = %output%
```

## Output Examples

```bash
TE: 108.1GB/140GB | Remain: 31.9GB | Used: 77%
```

Simple output (for Polybar):

```bash
108.1/140GB (31.9 left)
```

## Security Note

Always:

- Keep your config file private (chmod 600)
- Never commit your credentials to git
- Consider using a password manager for the credentials

## Contributing

Pull requests are welcome! If you have feature suggestions or find a bug, please open an issue.

## License

This project is licensed under the MIT License.

## Author

[Hany Mamdouh](https://github.com/hanymamdouh82)
