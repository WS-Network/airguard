export default async function Home(){
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001"}/healthz`, { cache: "no-store" });
  const data = await res.json();
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">AirGuard Web</h1>
      <pre className="mt-4 p-4 bg-gray-100 rounded">{JSON.stringify(data,null,2)}</pre>
    </main>
  );
}