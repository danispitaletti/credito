import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {Building, CamRig, Globe, IceBlock, Key3D, Stars, TERRA, TERRA_L, Vault, clamp01, ease, eio} from './three-parts';

const OW = '#F2EEE8';
const NAVY = '#1E3A5F', NAVY_L = '#3E6EA8', GREEN = '#3FAE6A', RED_CL = '#D52B1E', STAMP = '#C1272D', GOLD = '#D4AF6A', STEEL = '#A9AEB8';
const CH = '#0E0E10';
const W = 1080, H = 1920;

// ---------- fontes ----------
const fontHandle = delayRender('fontes');
Promise.all(
	[
		['Script', 'script.ttf'],
		['Sans', 'sans600.ttf', '600'],
		['Sans', 'sans700.ttf', '700'],
	].map(([fam, file, weight]) => {
		const f = new FontFace(fam, `url(${staticFile(file)})`, weight ? {weight} : {});
		return f.load().then((ff) => document.fonts.add(ff));
	}),
).then(() => continueRender(fontHandle));

// ---------- curvas ----------
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const keyed = (t: number, keys: number[][]) => {
	for (let i = 0; i < keys.length - 1; i++) {
		const a = keys[i], b = keys[i + 1];
		if (t >= a[0] && t <= b[0]) {
			const p = eio((t - a[0]) / (b[0] - a[0]));
			return a.slice(1).map((v, k) => lerp(v, b[k + 1], p));
		}
	}
	return keys[t < keys[0][0] ? 0 : keys.length - 1].slice(1);
};
const win = (t: number, a: number, b: number, fi = 0.35, fo = 0.3) => Math.min(ease((t - a) / fi), 1 - eio((t - (b - fo)) / fo));

// ---------- elementos 2D ----------
const Dot: React.FC<{c?: string}> = ({c = OW}) => (
	<span style={{display: 'inline-block', width: 12, height: 12, borderRadius: 6, background: c, marginRight: 14, verticalAlign: 'middle', boxShadow: `0 0 12px ${c}`}} />
);
const Label: React.FC<{children: React.ReactNode; p: number; style?: React.CSSProperties; c?: string}> = ({children, p, style, c}) => (
	<div style={{fontFamily: 'Sans', fontWeight: 600, fontSize: 30, letterSpacing: 6, color: OW, opacity: p, transform: `translateY(${(1 - p) * 14}px)`, textShadow: '0 2px 10px rgba(0,0,0,.6)', ...style}}>
		<Dot c={c} />
		{children}
	</div>
);
const Glass: React.FC<{p: number; style: React.CSSProperties; children?: React.ReactNode; tilt?: number}> = ({p, style, children, tilt = 0}) => (
	<div
		style={{
			position: 'absolute',
			borderRadius: 36,
			background: 'linear-gradient(160deg, rgba(34,34,40,.78), rgba(16,16,20,.82))',
			border: '1.5px solid rgba(255,255,255,.14)',
			boxShadow: '0 30px 80px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.08)',
			backdropFilter: 'blur(14px)',
			opacity: clamp01(p * 1.4),
			transform: `perspective(1400px) rotateX(${tilt + (1 - ease(p)) * 18}deg) translateY(${(1 - ease(p)) * 60}px) scale(${0.92 + 0.08 * ease(p)})`,
			overflow: 'hidden',
			...style,
		}}
	>
		{children}
	</div>
);
const Big: React.FC<{children: React.ReactNode; size: number; color?: string; p?: number; style?: React.CSSProperties}> = ({children, size, color = OW, p = 1, style}) => (
	<div style={{fontFamily: 'Sans', fontWeight: 700, fontSize: size, color, lineHeight: 0.95, letterSpacing: -1, opacity: clamp01(p * 1.5), transform: `translateY(${(1 - ease(p)) * 40}px) scale(${0.9 + 0.1 * ease(p)})`, textShadow: '0 10px 40px rgba(0,0,0,.55)', ...style}}>
		{children}
	</div>
);
const Script: React.FC<{children: React.ReactNode; size: number; p?: number; color?: string; style?: React.CSSProperties}> = ({children, size, p = 1, color = '#fff', style}) => (
	<div style={{fontFamily: 'Script', fontSize: size, color, opacity: clamp01(p * 1.5), transform: `translateY(${(1 - ease(p)) * 20}px)`, textShadow: '0 3px 14px rgba(0,0,0,.75)', ...style}}>{children}</div>
);

// ---------- legenda estilo Thiago: 1–3 palavras, branca, sem cor, sombra suave ----------
const CHUNKS: [string, number][][] = [
	[['Em', 0.256], ['menos', 0.427], ['de', 0.725]], [['um', 0.896], ['ano', 0.981]], [['de', 1.28], ['governo,', 1.408]],
	[['o', 2.133], ['Chile', 2.304], ['aprovou', 2.56]], [['uma', 2.987], ['das', 3.157], ['maiores', 3.285]], [['reformas', 3.797], ['tributárias', 4.352]],
	[['da', 5.035], ['América', 5.205]], [['do', 5.589], ['Sul.', 5.675]],
	[['O', 6.401], ['imposto', 6.87]], [['das', 7.297], ['empresas', 7.467]], [['vai', 7.979], ['cair', 8.15]], [['de', 8.534], ['27', 8.662]], [['para', 9.558], ['23%,', 9.814]], [['até', 11.265], ['2029.', 11.691]],
	[['Quem', 13.984], ['compra', 14.197]], [['imóvel', 14.539], ['novo', 14.923]], [['fica', 15.307], ['isento', 15.605]], [['de', 16.117], ['IVA', 16.245]], [['por', 16.544], ['um', 16.715], ['período.', 16.8]],
	[['E', 17.568], ['grandes', 17.995]], [['investimentos', 18.549]], [['ganham', 19.36], ['regras', 19.701]], [['congeladas', 20.085]], [['por', 20.853], ['até', 21.024]], [['20', 21.28], ['anos.', 21.792]],
	[['Resultado:', 23.099]], [['o', 23.91], ['Chile', 24.294], ['é', 24.72]], [['o', 24.805], ['17º', 24.891]], [['país', 25.957], ['mais', 26.384], ['livre', 26.811]], [['economicamente', 27.238]], [['do', 27.878], ['mundo.', 28.006]],
	[['O', 28.901], ['Brasil?', 29.072]], [['134º', 29.883]],
	[['Você', 32.721], ['não', 32.977], ['escolhe', 33.148]], [['as', 33.489], ['regras', 33.574]], [['do', 33.916], ['seu', 34.044], ['país.', 34.214]],
	[['Mas', 35.025], ['pode', 35.238], ['escolher', 35.452]], [['onde', 35.836], ['guarda', 36.049]], [['parte', 36.39], ['do', 36.902], ['seu', 36.988]], [['patrimônio.', 37.158]],
	[['Com', 38.097], ['autocustódia', 38.268]], [['em', 39.164], ['cripto,', 39.249]], [['a', 39.804], ['chave', 39.974]], [['é', 40.273], ['sua.', 40.358]],
	[['Autocustódia', 41.321]], [['é', 42.515], ['segurança', 42.729]], [['e', 43.582], ['proteção.', 43.838]],
];
const Caption: React.FC<{t: number; y?: number}> = ({t, y = 1500}) => {
	let idx = -1;
	for (let i = 0; i < CHUNKS.length; i++) if (t >= CHUNKS[i][0][1] - 0.05) idx = i;
	if (idx < 0) return null;
	const ch = CHUNKS[idx];
	const nextStart = idx + 1 < CHUNKS.length ? CHUNKS[idx + 1][0][1] : 45.0;
	const lastW = ch[ch.length - 1][1];
	const end = Math.min(nextStart, lastW + 0.9);
	if (t > end) return null;
	return (
		<div style={{position: 'absolute', left: 60, right: 60, top: y - 40, textAlign: 'center', fontFamily: 'Sans', fontWeight: 700, fontSize: 64, color: '#fff', letterSpacing: -0.5, textShadow: '0 3px 10px rgba(0,0,0,.75), 0 0 2px rgba(0,0,0,.6)'}}>
			{ch.map(([w, s], k) => {
				const p = ease((t - s) / 0.12);
				if (t < s - 0.03) return null;
				return (
					<span key={k} style={{display: 'inline-block', marginRight: 16, opacity: p, transform: `scale(${0.88 + 0.12 * p})`}}>
						{w}
					</span>
				);
			})}
		</div>
	);
};

// ---------- linha do tempo com marcador ----------
const Timeline: React.FC<{from: string; to: string; p: number; show: number; top: number}> = ({from, to, p, show, top}) => (
	<div style={{position: 'absolute', left: 120, right: 120, top, opacity: show}}>
		<div style={{height: 4, background: 'rgba(255,255,255,.15)', borderRadius: 2, position: 'relative'}}>
			<div style={{position: 'absolute', left: 0, top: 0, height: 4, width: `${p * 100}%`, background: NAVY_L, borderRadius: 2, boxShadow: `0 0 14px ${NAVY_L}`}} />
			<div style={{position: 'absolute', left: `calc(${p * 100}% - 11px)`, top: -9, width: 22, height: 22, borderRadius: 11, background: '#fff', boxShadow: `0 0 18px ${NAVY_L}`}} />
		</div>
		<div style={{display: 'flex', justifyContent: 'space-between', marginTop: 18, fontFamily: 'Sans', fontWeight: 600, fontSize: 28, color: OW, letterSpacing: 4}}>
			<span>{from}</span>
			<span style={{color: p > 0.98 ? GREEN : OW}}>{to}</span>
		</div>
	</div>
);

// ---------- partículas subindo (profundidade) ----------
const Dust: React.FC<{t: number; o?: number}> = ({t, o = 0.5}) => (
	<>
		{Array.from({length: 26}).map((_, i) => {
			const x = (i * 397) % W, sp = 20 + ((i * 53) % 40), s = 2 + (i % 4);
			const y = H - ((t * sp + i * 173) % (H + 100));
			return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: s, background: i % 3 ? '#ffffff' : '#cfd6e2', opacity: o * (0.3 + 0.7 * ((i % 5) / 5))}} />;
		})}
	</>
);

export const ChileVideo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = frame / fps;
	const [rede, setRede] = useState<any>(null);
	const [h] = useState(() => delayRender('rede'));
	useEffect(() => {
		fetch(staticFile('rede.json'))
			.then((r) => r.json())
			.then((j) => {
				setRede(j);
				continueRender(h);
			});
	}, [h]);

	// ---- câmera do globo ----
	const [lon, lat, dist, gy] = keyed(t, [
		[0, -25, -5, 4.6, 0],
		[2.1, -55, -18, 3.4, 0],
		[6.4, -71, -32, 1.9, 0],
		[13.98, -71, -36, 2.4, 0.55],
		[23.1, -64, -26, 2.8, 0.5],
		[28.9, -60, -22, 2.5, 0],
		[32.7, -50, -14, 2.1, 0],
		[38.1, -60, -22, 2.8, 0],
		[41.3, -60, -20, 3.3, 0.15],
		[45.6, -60, -20, 3.8, 0.15],
	]);
	const spin = t < 2.1 ? (2.1 - t) * 6 : 0;
	const chile = eio((t - 3.0) / 1.2);
	const brasil = eio((t - 29.3) / 1.0) * (1 - eio((t - 38.1) / 0.8));
	const redeP = eio((t - 38.0) / 2.6);
	// escurecimento do fundo nas cenas de painel
	const dim =
		Math.max(win(t, 6.4, 23.1, 0.4, 0.4) * 0.72, win(t, 23.1, 28.9, 0.3, 0.3) * 0.78, win(t, 32.7, 38.1, 0.4, 0.4) * 0.62, win(t, 41.3, 45.6, 0.4, 0.2) * 0.35);

	// ---- cenas ----
	const s3 = win(t, 6.4, 13.98), s4 = win(t, 13.98, 17.57, 0.3), s5 = win(t, 17.57, 23.1, 0.3), s6 = win(t, 23.1, 28.9, 0.3), s7 = win(t, 28.9, 32.7, 0.3), s8 = win(t, 32.7, 38.1, 0.3), s9 = win(t, 38.1, 41.4, 0.3, 0.25), s10 = win(t, 41.3, 46, 0.3);

	return (
		<AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 38%, #1d1612 0%, ${CH} 60%)`}}>
			{/* ===== globo 3D ===== */}
			<AbsoluteFill style={{transform: `translateY(${gy * 300}px)`, filter: `blur(${10 * win(t, 3.7, 6.5, 0.35, 0.4)}px) brightness(${1 - 0.35 * win(t, 3.7, 6.5, 0.35, 0.4)})`}}>
				<ThreeCanvas width={W} height={H} gl={{antialias: true}}>
					<CamRig pos={[0, -0.18 * dist, dist]} look={[0, 0, 0]} fov={38} />
					<ambientLight intensity={0.45} />
					<directionalLight position={[-3, 2.5, 4]} intensity={2.4} />
					<directionalLight position={[4, -1, -2]} intensity={0.6} color="#9fb7d6" />
					<Stars opacity={0.75} />
					<Globe lon={lon - spin} lat={lat} chile={chile} brasil={brasil} rede={rede} redeP={redeP} time={t} />
				</ThreeCanvas>
			</AbsoluteFill>
			<AbsoluteFill style={{background: CH, opacity: dim}} />
			<Dust t={t} o={0.35} />

			{/* ===== S1: contador de dias ===== */}
			{t < 2.4 ? (
				<AbsoluteFill style={{opacity: 1 - eio((t - 2.0) / 0.4)}}>
					<Label c={RED_CL} p={ease((t - 0.1) / 0.4)} style={{position: 'absolute', top: 300, width: '100%', textAlign: 'center'}}>
						CHILE · 2026
					</Label>
					<Big size={170} p={ease((t - 0.2) / 0.4)} style={{position: 'absolute', top: 360, width: '100%', textAlign: 'center'}}>
						{Math.round(lerp(0, 300, eio(t / 1.9)))}
						<span style={{fontSize: 60, color: STEEL, marginLeft: 16}}>DIAS</span>
					</Big>
				</AbsoluteFill>
			) : null}

			{/* ===== S2: REFORMA + carimbo ===== */}
			{t >= 2.1 && t < 6.6 ? (
				<AbsoluteFill style={{opacity: win(t, 2.1, 6.6, 0.3, 0.3)}}>
					<Big size={176} color="rgba(242,238,232,.92)" p={ease((t - 3.75) / 0.35)} style={{position: 'absolute', top: 300, width: '100%', textAlign: 'center', letterSpacing: 4}}>
						REFORMA
					</Big>
					{t > 4.3 ? (
						<div
							style={{
								position: 'absolute',
								top: 500,
								left: 0,
								right: 0,
								textAlign: 'center',
								transform: `rotate(-8deg) scale(${lerp(2.2, 1, ease((t - 4.3) / 0.18))})`,
								opacity: clamp01((t - 4.3) / 0.08),
							}}
						>
							<span style={{fontFamily: 'Sans', fontWeight: 700, fontSize: 80, letterSpacing: 10, color: STAMP, border: `8px solid ${STAMP}`, borderRadius: 18, padding: '6px 34px', boxShadow: `0 0 40px rgba(193,39,45,.35)`, background: 'rgba(14,14,16,.35)'}}>
								APROVADA
							</span>
						</div>
					) : null}
				</AbsoluteFill>
			) : null}

			{/* ===== S3: imposto 27 -> 23 + prédio ===== */}
			{s3 > 0 ? (
				<AbsoluteFill style={{opacity: s3}}>
					<Glass p={ease((t - 6.5) / 0.45)} style={{left: 70, right: 70, top: 250, height: 650}}>
						<Label c={NAVY_L} p={ease((t - 6.7) / 0.3)} style={{position: 'absolute', top: 44, left: 50}}>
							IMPOSTO DAS EMPRESAS
						</Label>
						{/* barras */}
						{(() => {
							const q = eio((t - 8.6) / 1.8);
							const v = lerp(27, 23, q);
							return (
								<>
									<div style={{position: 'absolute', left: 70, bottom: 190, width: 150, height: 27 * 11, background: 'rgba(255,255,255,.12)', borderRadius: 14}} />
									<div style={{position: 'absolute', left: 70, bottom: 190, width: 150, height: v * 11 * ease((t - 6.8) / 0.6), background: `linear-gradient(180deg, ${NAVY_L}, ${NAVY})`, borderRadius: 14, boxShadow: `0 0 40px rgba(62,110,168,.45)`}} />
									<Big size={220} style={{position: 'absolute', left: 270, top: 130}} color={q > 0.98 ? GREEN : OW}>
										{Math.round(v)}%
									</Big>
									<div style={{position: 'absolute', left: 280, top: 360, fontFamily: 'Sans', fontWeight: 600, fontSize: 30, color: 'rgba(242,238,232,.7)', letterSpacing: 4, opacity: ease((t - 10.4) / 0.3)}}>
										ERA 27%
									</div>
								</>
							);
						})()}
						<div style={{position: 'absolute', left: 0, right: 0, top: 480}}>
							<Timeline from="2026" to="2029" p={eio((t - 10.6) / 1.6)} show={ease((t - 10.4) / 0.3)} top={0} />
						</div>
					</Glass>
					<div style={{position: 'absolute', left: 0, right: 0, top: 1080, height: 700, opacity: ease((t - 6.9) / 0.4)}}>
						<ThreeCanvas width={W} height={700}>
							<CamRig pos={[2.6, 2.2, 3.4]} look={[0, 1.1, 0]} fov={40} />
							<ambientLight intensity={0.5} />
							<directionalLight position={[3, 5, 2]} intensity={2} />
							<pointLight position={[-2, 1, 2]} intensity={6} color={NAVY_L} />
							<Building floors={14} p={eio((t - 7.0) / 5.0)} time={t} />
						</ThreeCanvas>
					</div>
					<Label p={ease((t - 7.2) / 0.3)} style={{position: 'absolute', top: 1720, width: '100%', textAlign: 'center', fontSize: 26}}>
						EMPRESAS NO CHILE
					</Label>
				</AbsoluteFill>
			) : null}

			{/* ===== S4: imóvel novo, IVA isento ===== */}
			{s4 > 0 ? (
				<AbsoluteFill style={{opacity: s4}}>
					<div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 760}}>
						<ThreeCanvas width={W} height={760}>
							<CamRig pos={[-2.4, 1.8, 3.2]} look={[0, 0.8, 0]} fov={40} />
							<ambientLight intensity={0.5} />
							<directionalLight position={[3, 5, 2]} intensity={2} />
							<pointLight position={[2, 1, 2]} intensity={5} color="#ffb070" />
							<Building floors={8} p={eio((t - 14.0) / 1.6)} time={t} warm />
						</ThreeCanvas>
					</div>
					<Glass p={ease((t - 14.1) / 0.4)} style={{left: 140, right: 140, top: 260, height: 380}} tilt={4}>
						<Label p={ease((t - 14.3) / 0.3)} style={{position: 'absolute', top: 40, left: 46}}>
							IMÓVEL NOVO
						</Label>
						<div style={{position: 'absolute', left: 46, top: 110, fontFamily: 'Sans', fontWeight: 700, fontSize: 150, color: OW, opacity: ease((t - 14.4) / 0.3)}}>
							IVA <span style={{color: t > 15.9 ? GREEN : OW}}>{t > 15.9 ? '0%' : '19%'}</span>
						</div>
						<div style={{position: 'absolute', left: 40, top: 205, height: 14, width: 700 * eio((t - 15.6) / 0.3), background: STAMP, borderRadius: 7, boxShadow: `0 0 18px ${STAMP}`, opacity: t > 15.9 ? 0 : 1}} />
						<Big size={70} color={GREEN} p={ease((t - 15.95) / 0.3)} style={{position: 'absolute', right: 50, top: 270, letterSpacing: 6}}>
							ISENTO
						</Big>
					</Glass>
				</AbsoluteFill>
			) : null}

			{/* ===== S5: grandes investimentos, 20 anos congelados ===== */}
			{s5 > 0 ? (
				<AbsoluteFill style={{opacity: s5}}>
					<Label p={ease((t - 17.7) / 0.3)} style={{position: 'absolute', top: 270, left: 90}}>
						GRANDES INVESTIMENTOS
					</Label>
					<div style={{position: 'absolute', left: 90, top: 330, opacity: ease((t - 18.4) / 0.3), transform: `scale(${0.8 + 0.2 * ease((t - 18.4) / 0.3)})`, transformOrigin: 'left center'}}>
						<span style={{fontFamily: 'Sans', fontWeight: 700, fontSize: 46, color: CH, background: OW, padding: '8px 22px', borderRadius: 40}}>US$ 350 MI+</span>
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, top: 420, height: 640}}>
						<ThreeCanvas width={W} height={640}>
							<CamRig pos={[0, 0, 4]} fov={35} />
							<ambientLight intensity={0.6} />
							<directionalLight position={[2, 3, 4]} intensity={2.2} />
							<pointLight position={[-2, -1, 2]} intensity={4} color="#9fd2ff" />
							<IceBlock freeze={eio((t - 20.0) / 0.8)} time={t} />
						</ThreeCanvas>
					</div>
					{t > 20.0 ? (
						<>
							{Array.from({length: 18}).map((_, i) => {
								const a = (i / 18) * Math.PI * 2, r = 200 + 160 * ease((t - 20.0) / 0.8);
								return <div key={i} style={{position: 'absolute', left: 540 + Math.cos(a) * r, top: 740 + Math.sin(a) * r * 0.9, width: 8, height: 8, borderRadius: 4, background: '#e8f6ff', opacity: 1 - eio((t - 20.6) / 0.8), boxShadow: '0 0 12px #bfe4ff'}} />;
							})}
						</>
					) : null}
					<div style={{position: 'absolute', left: 0, right: 0, top: 1080, textAlign: 'center'}}>
						<Big size={200} color={t > 21.7 ? '#9fd2ff' : OW} p={ease((t - 20.9) / 0.3)}>
							{Math.round(lerp(0, 20, eio((t - 21.0) / 0.8)))}
							<span style={{fontSize: 70, marginLeft: 18}}>ANOS</span>
						</Big>
					</div>
					<Timeline from="2026" to="2046" p={eio((t - 21.0) / 1.4)} show={ease((t - 20.9) / 0.3)} top={1320} />
				</AbsoluteFill>
			) : null}

			{/* ===== S6: ranking ===== */}
			{s6 > 0 ? (
				<AbsoluteFill style={{opacity: s6}}>
					<Label p={ease((t - 23.2) / 0.3)} style={{position: 'absolute', top: 260, width: '100%', textAlign: 'center'}}>
						LIBERDADE ECONÔMICA · MUNDO
					</Label>
					{(() => {
						const scroll = eio((t - 24.6) / 1.5);
						const rowH = 92;
						return (
							<div style={{position: 'absolute', left: 90, right: 90, top: 340, height: 980, overflow: 'hidden', maskImage: 'linear-gradient(180deg, transparent, #000 12%, #000 88%, transparent)'}}>
								<div style={{transform: `translateY(${-scroll * 11 * rowH}px)`}}>
									{Array.from({length: 26}).map((_, i) => {
										const rank = i + 1, isC = rank === 17;
										const p = ease((t - 23.4 - i * 0.04) / 0.35);
										const w = 860 - rank * 18;
										return (
											<div key={i} style={{display: 'flex', alignItems: 'center', height: rowH, opacity: p, transform: `translateX(${(1 - p) * -60}px)`}}>
												<div style={{width: 110, fontFamily: 'Sans', fontWeight: 700, fontSize: 38, color: isC ? RED_CL : 'rgba(242,238,232,.55)'}}>{rank}º</div>
												<div style={{height: 46, width: w * p, borderRadius: 12, background: isC ? `linear-gradient(90deg, #A11F15, ${RED_CL})` : 'rgba(255,255,255,.12)', boxShadow: isC ? `0 0 40px rgba(213,43,30,.5)` : 'none', display: 'flex', alignItems: 'center', paddingLeft: 24, fontFamily: 'Sans', fontWeight: 700, fontSize: 34, color: '#fff', letterSpacing: 4}}>
													{isC ? 'CHILE' : ''}
												</div>
											</div>
										);
									})}
								</div>
							</div>
						);
					})()}
				</AbsoluteFill>
			) : null}

			{/* ===== S7: Brasil 134º ===== */}
			{s7 > 0 ? (
				<AbsoluteFill style={{opacity: s7}}>
					<Glass p={ease((t - 29.0) / 0.4)} style={{left: 90, width: 420, top: 270, height: 330}}>
						<Label p={1} c={RED_CL} style={{position: 'absolute', top: 36, left: 36, fontSize: 24}}>
							CHILE
						</Label>
						<Big size={150} color={RED_CL} style={{position: 'absolute', left: 36, top: 100}}>17º</Big>
					</Glass>
					<Glass p={ease((t - 29.4) / 0.4)} style={{right: 90, width: 420, top: 270, height: 330}}>
						<Label p={1} c="#009C3B" style={{position: 'absolute', top: 36, left: 36, fontSize: 24}}>
							BRASIL
						</Label>
						<Big size={150} color="#a9a9ae" style={{position: 'absolute', left: 36, top: 100}}>
							{Math.round(lerp(17, 134, eio((t - 29.9) / 1.6)))}º
						</Big>
					</Glass>
					<div style={{position: 'absolute', left: 90, right: 90, top: 650, height: 10, borderRadius: 5, background: 'rgba(255,255,255,.12)', opacity: ease((t - 29.6) / 0.3)}}>
						<div style={{width: `${(eio((t - 29.9) / 1.6) * 117 + 17) / 1.84}%`, height: 10, borderRadius: 5, background: 'linear-gradient(90deg,#a9a9ae,#55555a)'}} />
					</div>
				</AbsoluteFill>
			) : null}

			{/* ===== S8: você escolhe onde guarda ===== */}
			{s8 > 0 ? (
				<AbsoluteFill style={{opacity: s8}}>
					<div style={{position: 'absolute', left: 0, right: 0, top: 820, height: 760, opacity: ease((t - 33.0) / 0.5)}}>
						<ThreeCanvas width={W} height={760}>
							<CamRig pos={[0.6, 0.3, 4.2]} fov={36} />
							<ambientLight intensity={0.5} />
							<directionalLight position={[2, 3, 4]} intensity={2.4} />
							<pointLight position={[-2, 1, 2]} intensity={6} color="#ffd9b0" />
							<Vault close={eio((t - 35.9) / 1.3)} spin={eio((t - 37.1) / 0.9)} />
						</ThreeCanvas>
					</div>
					<div style={{position: 'absolute', left: 90, top: 290}}>
						<Label p={ease((t - 33.4) / 0.3)} c="#8a8a90">REGRAS DO PAÍS</Label>
						<div style={{fontFamily: 'Sans', fontWeight: 700, fontSize: 64, color: '#8a8a90', marginTop: 6, opacity: ease((t - 33.5) / 0.25)}}>
							✕ <span style={{fontSize: 40, letterSpacing: 4}}>VOCÊ NÃO ESCOLHE</span>
						</div>
					</div>
					<div style={{position: 'absolute', left: 90, top: 470}}>
						<Label c={GOLD} p={ease((t - 35.4) / 0.3)}>ONDE VOCÊ GUARDA</Label>
						<div style={{fontFamily: 'Sans', fontWeight: 700, fontSize: 64, color: GOLD, marginTop: 6, opacity: ease((t - 35.5) / 0.25)}}>
							✓ <span style={{fontSize: 40, letterSpacing: 4}}>VOCÊ ESCOLHE</span>
						</div>
					</div>
				</AbsoluteFill>
			) : null}

			{/* ===== S9: a chave é sua ===== */}
			{t >= 38.0 ? (
				<AbsoluteFill style={{opacity: Math.min(1, ease((t - 39.7) / 0.3))}}>
					<div style={{position: 'absolute', left: 0, right: 0, top: 230, height: 620}}>
						<ThreeCanvas width={W} height={620}>
							<CamRig pos={[0, 0, 3.4]} fov={35} />
							<ambientLight intensity={0.6} />
							<directionalLight position={[2, 3, 4]} intensity={2.6} />
							<pointLight position={[-2, -1, 2]} intensity={6} color="#ffb090" />
							<Key3D p={(t - 39.8) / 0.6} time={t} />
						</ThreeCanvas>
					</div>
				</AbsoluteFill>
			) : null}
			{s9 > 0 ? (
				<AbsoluteFill style={{opacity: s9}}>
					<Label c={GOLD} p={ease((t - 39.85) / 0.3)} style={{position: 'absolute', top: 860, width: '100%', textAlign: 'center'}}>
						AUTOCUSTÓDIA
					</Label>
					<Big size={150} p={ease((t - 39.95) / 0.3)} style={{position: 'absolute', top: 920, width: '100%', textAlign: 'center'}}>
						A CHAVE <span style={{color: GOLD}}>É SUA</span>
					</Big>
				</AbsoluteFill>
			) : null}

			{/* ===== S10: recapitulação + fechamento ===== */}
			{s10 > 0 ? (
				<AbsoluteFill style={{opacity: s10}}>
					{(() => {
						const g = ease((t - 41.3) / 0.3) * (1 - eio((t - 42.15) / 0.3));
						const items = [
							['REFORMA', 'Chile'],
							['23%', 'imposto'],
							['17º', 'liberdade'],
							['CHAVE', 'sua'],
						];
						return items.map(([a, b], k) => {
							const x = k % 2 ? 560 : 100, y = k < 2 ? 900 : 1180;
							const dx = (k % 2 ? 1 : -1) * (1 - g) * 120;
							return (
								<Glass key={k} p={g} style={{left: x + dx, top: y, width: 420, height: 250}}>
									<Big size={84} color={[RED_CL, GREEN, RED_CL, GOLD][k]} style={{position: 'absolute', left: 34, top: 50}}>{a}</Big>
									<div style={{position: 'absolute', left: 38, top: 160, fontFamily: 'Sans', fontWeight: 600, fontSize: 30, letterSpacing: 5, color: 'rgba(242,238,232,.75)'}}>{b.toUpperCase()}</div>
								</Glass>
							);
						});
					})()}
					<Big size={128} p={ease((t - 42.2) / 0.35)} style={{position: 'absolute', top: 900, width: '100%', textAlign: 'center', letterSpacing: 2}}>
						AUTOCUSTÓDIA
					</Big>
					<Big size={96} p={ease((t - 42.7) / 0.35)} style={{position: 'absolute', top: 1050, width: '100%', textAlign: 'center', letterSpacing: 6}}>
						É SEGURANÇA
					</Big>
					<Big size={96} color={GOLD} p={ease((t - 43.75) / 0.35)} style={{position: 'absolute', top: 1220, width: '100%', textAlign: 'center', letterSpacing: 6}}>
						E PROTEÇÃO
					</Big>
				</AbsoluteFill>
			) : null}

			<Caption t={t} />

			{/* fade final */}
			<AbsoluteFill style={{background: CH, opacity: eio((t - 45.0) / 0.6)}} />
		</AbsoluteFill>
	);
};
