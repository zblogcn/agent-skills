import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, basename, resolve } from 'node:path';

const dir = resolve(process.argv[2] || '.');

const result = {
  path: dir,
  type: 'unknown',
  database: null,
  table_prefix: null,
  current_theme: null,
  using_plugins: [],
  plugins: [],
  themes: [],
  app_id: null,
  app_name: null,
};

const read = (p) => {
  try { return readFileSync(p, 'utf8'); } catch { return null; }
};
const lsdir = (p) => {
  try { return readdirSync(p, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name); } catch { return []; }
};

// 1. 判定类型
const isSiteRoot = existsSync(join(dir, 'zb_system')) && existsSync(join(dir, 'zb_users'))
  && existsSync(join(dir, 'zb_system', 'function', 'c_system_base.php'));
const pluginXml = read(join(dir, 'plugin.xml'));
const themeXml = read(join(dir, 'theme.xml'));

if (isSiteRoot) {
  result.type = 'site_root';
} else if (pluginXml && pluginXml.includes('<plugin')) {
  result.type = 'plugin';
  result.app_id = (pluginXml.match(/<id>([^<]+)<\/id>/) || [])[1] || null;
  result.app_name = (pluginXml.match(/<name>([^<]+)<\/name>/) || [])[1] || null;
} else if (themeXml && themeXml.includes('<theme')) {
  result.type = 'theme';
  result.app_id = (themeXml.match(/<id>([^<]+)<\/id>/) || [])[1] || null;
  result.app_name = (themeXml.match(/<name>([^<]+)<\/name>/) || [])[1] || null;
}

// 2. 站点根：读配置、插件/主题清单
if (result.type === 'site_root') {
  const opt = read(join(dir, 'zb_users', 'c_option.php'));
  if (opt) {
    result.database = (opt.match(/'ZC_DATABASE_TYPE'\s*=>\s*'([^']+)'/) || opt.match(/ZC_DATABASE_TYPE'?\s*,\s*'([^']+)'/) || [])[1] || null;
    result.table_prefix = (opt.match(/'ZC_MYSQL_PRE'\s*=>\s*'([^']+)'/) || [])[1] || null;
    result.current_theme = (opt.match(/'ZC_BLOG_THEME'\s*=>\s*'([^']+)'/) || [])[1] || null;
    const using = (opt.match(/'ZC_USING_PLUGIN_LIST'\s*=>\s*'([^']*)'/) || [])[1] || '';
    result.using_plugins = using.split('|').filter(Boolean);
  }
  result.plugins = lsdir(join(dir, 'zb_users', 'plugin'));
  result.themes = lsdir(join(dir, 'zb_users', 'theme'));
}

console.log(JSON.stringify(result, null, 2));
