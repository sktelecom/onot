export function Preview({ html, title }: { html: string; title: string }) {
  // iframe srcdoc + sandbox로 미리보기를 격리(CSS 충돌/스크립트 차단)
  return (
    <iframe
      title={title}
      srcDoc={html}
      sandbox=""
      className="h-[60vh] w-full rounded-lg border border-zinc-200 bg-white dark:border-zinc-800"
    />
  );
}
