import 'bootstrap/dist/css/bootstrap.min.css';
import "./globals.css";



export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header className="my-4">
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
