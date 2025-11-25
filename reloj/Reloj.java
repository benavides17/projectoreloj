import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.geom.Point2D;
import java.time.*;
import java.util.LinkedHashMap;
import java.util.Map;

public class Reloj {
    static final String APP = "Reloj Java - Todo en uno";
    static final int REFRESH_MS = 200;

    static class Lang {
        String[] weekdays;
        String[] months;
        String fmt;
        Lang(String[] w, String[] m, String f) { weekdays = w; months = m; fmt = f; }
    }

    static final Map<String, Lang> LANGS = new LinkedHashMap<>();
    static {
        LANGS.put("es", new Lang(new String[]{"lunes","martes","miércoles","jueves","viernes","sábado","domingo"},
                new String[]{"enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"},
                "{weekday}, {day} de {month} de {year}"));
        LANGS.put("en", new Lang(new String[]{"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"},
                new String[]{"January","February","March","April","May","June","July","August","September","October","November","December"},
                "{weekday}, {month} {day}, {year}"));
        LANGS.put("pt", new Lang(new String[]{"segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"},
                new String[]{"janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"},
                "{weekday}, {day} de {month} de {year}"));
        LANGS.put("fr", new Lang(new String[]{"lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"},
                new String[]{"janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"},
                "{weekday} {day} {month} {year}"));
    }

    static String fmtDateLocalized(ZonedDateTime now, String lang) {
        Lang l = LANGS.getOrDefault(lang, LANGS.get("es"));
        String wd = l.weekdays[now.getDayOfWeek().getValue() - 1];
        String mo = l.months[now.getMonthValue() - 1];
        String s = l.fmt.replace("{weekday}", wd)
                .replace("{day}", String.format("%02d", now.getDayOfMonth()))
                .replace("{month}", mo)
                .replace("{year}", Integer.toString(now.getYear()));
        return s.substring(0, 1).toUpperCase() + s.substring(1);
    }

    static String fmtHhmmss(int seconds) {
        int h = seconds / 3600;
        int m = (seconds % 3600) / 60;
        int ss = seconds % 60;
        return String.format("%02d:%02d:%02d", h, m, ss);
    }

    static class AnalogClock extends JPanel {
        int size;
        int r;
        Color bg;
        Color fg;
        Color accent;
        ZonedDateTime current;

        AnalogClock(int size, Color bg, Color fg, Color accent) {
            this.size = size;
            this.r = size / 2 - 10;
            this.bg = bg;
            this.fg = fg;
            this.accent = accent;
            setPreferredSize(new Dimension(size, size));
            setBackground(bg);
        }

        void setTheme(Color bg, Color fg, Color accent) {
            this.bg = bg;
            this.fg = fg;
            this.accent = accent == null ? this.accent : accent;
            setBackground(bg);
            repaint();
        }

        void updateTime(ZonedDateTime now) {
            this.current = now;
            repaint();
        }

        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            int s = size;
            int rr = r;
            g2.setColor(bg);
            g2.fillRect(0, 0, s, s);
            g2.setColor(fg);
            g2.setStroke(new BasicStroke(2f));
            g2.drawOval(10, 10, s - 20, s - 20);
            for (int i = 0; i < 60; i++) {
                double ang = Math.toRadians(i * 6);
                double x0 = s / 2.0 + (rr - 10) * Math.sin(ang);
                double y0 = s / 2.0 - (rr - 10) * Math.cos(ang);
                int length = i % 5 == 0 ? 12 : 5;
                double x1 = s / 2.0 + (rr - 10 - length) * Math.sin(ang);
                double y1 = s / 2.0 - (rr - 10 - length) * Math.cos(ang);
                g2.setStroke(new BasicStroke(i % 5 == 0 ? 2f : 1f));
                g2.drawLine((int) x0, (int) y0, (int) x1, (int) y1);
            }
            g2.setFont(new Font("SansSerif", Font.BOLD, 12));
            for (int h = 1; h <= 12; h++) {
                double ang = Math.toRadians(h * 30);
                double x = s / 2.0 + (rr - 30) * Math.sin(ang);
                double y = s / 2.0 - (rr - 30) * Math.cos(ang);
                String t = Integer.toString(h);
                FontMetrics fm = g2.getFontMetrics();
                int w = fm.stringWidth(t);
                int ascent = fm.getAscent();
                g2.drawString(t, (int) (x - w / 2.0), (int) (y + ascent / 2.0));
            }
            g2.setColor(fg);
            g2.fillOval(s / 2 - 4, s / 2 - 4, 8, 8);
            if (current != null) {
                double h = (current.getHour() % 12) + current.getMinute() / 60.0 + current.getSecond() / 3600.0;
                double m = current.getMinute() + current.getSecond() / 60.0;
                double sec = current.getSecond() + current.getNano() / 1e9;
                Point2D.Double hp = endpoint(s, h * 30, rr * 0.5);
                Point2D.Double mp = endpoint(s, m * 6, rr * 0.72);
                Point2D.Double sp = endpoint(s, sec * 6, rr * 0.82);
                g2.setStroke(new BasicStroke(4f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                g2.setColor(fg);
                g2.drawLine(s / 2, s / 2, (int) hp.x, (int) hp.y);
                g2.setStroke(new BasicStroke(3f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                g2.drawLine(s / 2, s / 2, (int) mp.x, (int) mp.y);
                g2.setStroke(new BasicStroke(1f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                g2.setColor(accent);
                g2.drawLine(s / 2, s / 2, (int) sp.x, (int) sp.y);
            }
            g2.dispose();
        }

        static Point2D.Double endpoint(int s, double deg, double length) {
            double ang = Math.toRadians(deg);
            double x = s / 2.0 + length * Math.sin(ang);
            double y = s / 2.0 - length * Math.cos(ang);
            return new Point2D.Double(x, y);
        }
    }

    static class App extends JFrame {
        JCheckBox is24h;
        JCheckBox dark;
        JComboBox<String> lang;
        JComboBox<String> tz;
        JLabel lbl;
        JLabel ampmLbl;
        JLabel dateLbl;
        AnalogClock analog;
        boolean colonOn = true;
        Integer lastSecond = null;
        Integer lastHourChime = null;

        App() {
            super(APP);
            setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
            setSize(1000, 680);
            setLocationRelativeTo(null);

            is24h = new JCheckBox("24h", true);
            dark = new JCheckBox("Oscuro", false);
            lang = new JComboBox<>(LANGS.keySet().toArray(new String[0]));
            lang.setSelectedItem("es");
            tz = new JComboBox<>(new String[]{"local","UTC","Europe/Madrid","Europe/Paris","America/Mexico_City","America/Bogota","America/Sao_Paulo"});
            tz.setSelectedItem("local");

            JPanel topbar = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 8));
            topbar.add(is24h);
            topbar.add(dark);
            topbar.add(new JLabel("Idioma:"));
            topbar.add(lang);
            topbar.add(new JLabel("Zona:"));
            topbar.add(tz);

            JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT, 20, 12));
            lbl = new JLabel("00:00:00");
            lbl.setFont(new Font("SansSerif", Font.BOLD, 72));
            top.add(lbl);
            ampmLbl = new JLabel("");
            ampmLbl.setFont(new Font("SansSerif", Font.PLAIN, 24));
            top.add(ampmLbl);
            analog = new AnalogClock(320, Color.decode("#f7f7f7"), Color.decode("#1a1a1a"), Color.decode("#e11d48"));
            top.add(analog);

            JPanel bottom = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 12));
            dateLbl = new JLabel("");
            dateLbl.setFont(new Font("SansSerif", Font.PLAIN, 20));
            bottom.add(dateLbl);

            setLayout(new BorderLayout());
            add(topbar, BorderLayout.NORTH);
            add(top, BorderLayout.CENTER);
            add(bottom, BorderLayout.SOUTH);

            dark.addActionListener(e -> applyColors());
            lang.addActionListener(e -> renderDate());
            tz.addActionListener(e -> renderDate());

            applyColors();
            renderDate();

            Timer timer = new Timer(REFRESH_MS, (ActionEvent e) -> tick());
            timer.start();
        }

        void applyColors() {
            boolean d = dark.isSelected();
            Color bg = d ? Color.decode("#0f172a") : Color.decode("#f7f7f7");
            Color fg = d ? Color.decode("#e5e7eb") : Color.decode("#1a1a1a");
            Color accent = Color.decode("#e11d48");
            getContentPane().setBackground(bg);
            for (Component c : getContentPane().getComponents()) c.setBackground(bg);
            lbl.setForeground(fg);
            ampmLbl.setForeground(fg);
            dateLbl.setForeground(fg);
            is24h.setBackground(bg); is24h.setForeground(fg);
            dark.setBackground(bg); dark.setForeground(fg);
            lang.setBackground(bg); lang.setForeground(fg);
            tz.setBackground(bg); tz.setForeground(fg);
            analog.setTheme(bg, fg, accent);
            renderDate();
        }

        ZonedDateTime getNow() {
            String zone = (String) tz.getSelectedItem();
            try {
                ZoneId id = "local".equals(zone) ? ZoneId.systemDefault() : ZoneId.of(zone);
                return ZonedDateTime.now(id);
            } catch (Exception ex) {
                return ZonedDateTime.now();
            }
        }

        void renderDate() {
            ZonedDateTime now = getNow();
            String l = (String) lang.getSelectedItem();
            dateLbl.setText(fmtDateLocalized(now, l));
        }

        String[] formatTime(ZonedDateTime now) {
            boolean h24 = is24h.isSelected();
            int h = h24 ? now.getHour() : (now.getHour() % 12 == 0 ? 12 : now.getHour() % 12);
            String ampm = h24 ? "" : (now.getHour() < 12 ? "AM" : "PM");
            int m = now.getMinute();
            int s = now.getSecond();
            if (lastSecond == null || !lastSecond.equals(s)) {
                colonOn = !colonOn;
                lastSecond = s;
            }
            String sep = colonOn ? ":" : " ";
            return new String[]{String.format("%02d%s%02d%s%02d", h, sep, m, sep, s), ampm};
        }

        void tick() {
            ZonedDateTime now = getNow();
            String[] t = formatTime(now);
            lbl.setText(t[0]);
            ampmLbl.setText(is24h.isSelected() ? "" : t[1]);
            analog.updateTime(now);
            if (now.getMinute() == 0 && now.getSecond() == 0) {
                if (lastHourChime == null || lastHourChime != now.getHour()) {
                    try { Toolkit.getDefaultToolkit().beep(); } catch (Exception ignored) {}
                    lastHourChime = now.getHour();
                }
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new App().setVisible(true));
    }
}

