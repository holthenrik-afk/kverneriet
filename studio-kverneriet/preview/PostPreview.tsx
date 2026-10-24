// Fanen «Forhåndsvisning» på blogginnlegg. Viser utkastet slik det blir seende ut på
// kverneriet.no, og oppdateres mens du skriver. Se postHtml.ts for hvorfor den tegner selv.
import {useEffect, useRef, useState} from 'react'
import {Box, Button, Card, Flex, Text} from '@sanity/ui'
import {postBody, postShell} from './postHtml'

type Props = {document: {displayed?: any; draft?: any; published?: any}}

const BREDDER = {mobil: 390, pc: '100%'} as const
type Visning = keyof typeof BREDDER

// Rammen lages én gang. Endres den, laster nettleseren siden på nytt og den hopper til toppen.
const SHELL = postShell()

export function PostPreview({document}: Props) {
  const ramme = useRef<HTMLIFrameElement>(null)
  const [klar, setKlar] = useState(false)
  const [visning, setVisning] = useState<Visning>('pc')
  const doc = document.displayed
  const harUtkast = Boolean(document.draft)

  // Bytt bare innholdet i <body>, så rulleposisjonen står der den står mens du skriver.
  useEffect(() => {
    const d = ramme.current?.contentDocument
    if (!klar || !d?.body) return
    const t = setTimeout(() => (d.body.innerHTML = postBody(doc)), 150)
    return () => clearTimeout(t)
  }, [doc, klar])

  return (
    <Flex direction="column" height="fill">
      <Card padding={3} borderBottom tone={harUtkast ? 'caution' : 'default'}>
        <Flex align="center" gap={3} wrap="wrap">
          <Box flex={1}>
            <Text size={1} weight="medium">
              {harUtkast
                ? 'Du ser utkastet. Ingenting er ute på kverneriet.no før du trykker Publish.'
                : 'Du ser det som er publisert.'}
            </Text>
          </Box>
          <Flex gap={1}>
            <Button text="PC" mode={visning === 'pc' ? 'default' : 'ghost'} onClick={() => setVisning('pc')} fontSize={1} padding={2} />
            <Button text="Mobil" mode={visning === 'mobil' ? 'default' : 'ghost'} onClick={() => setVisning('mobil')} fontSize={1} padding={2} />
          </Flex>
        </Flex>
      </Card>
      <Card flex={1} tone="transparent" style={{overflow: 'auto', display: 'flex', justifyContent: 'center'}}>
        <iframe
          ref={ramme}
          title="Forhåndsvisning av innlegget"
          srcDoc={SHELL}
          onLoad={() => setKlar(true)}
          style={{
            width: BREDDER[visning],
            maxWidth: '100%',
            height: '100%',
            minHeight: 600,
            border: 0,
            background: '#fff',
            boxShadow: visning === 'mobil' ? '0 0 0 1px rgba(0,0,0,.12)' : 'none',
          }}
        />
      </Card>
    </Flex>
  )
}
