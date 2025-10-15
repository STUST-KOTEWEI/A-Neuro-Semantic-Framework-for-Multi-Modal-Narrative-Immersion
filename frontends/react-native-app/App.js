import React, { useEffect, useState, useCallback } from 'react';
import { SafeAreaView, Text, FlatList, TouchableOpacity, StyleSheet, View } from 'react-native';
import axios from 'axios';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8010';
const API_KEY = process.env.API_KEY || 'dev-key-123';

export default function App() {
  const [status, setStatus] = useState('初始化...');
  const [files, setFiles] = useState([]);
  const [etag, setEtag] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState(null);

  const loadManifest = useCallback(async (force=false) => {
    try {
      setStatus('同步 manifest 中...');
      const headers = { 'X-API-Key': API_KEY };
      if (!force && etag) headers['If-None-Match'] = etag;
      const resp = await axios.get(`${BASE_URL}/sync/manifest`, { headers, validateStatus: () => true });
      if (resp.status === 304) { setStatus('無變更'); return; }
      if (resp.status !== 200) { setStatus('Manifest 錯誤 ' + resp.status); return; }
      setEtag(resp.data.etag);
      setFiles(resp.data.files);
      setStatus(`同步完成 files=${resp.data.file_count}`);
    } catch (e) {
      setStatus('同步失敗: ' + e.message);
    }
  }, [etag]);

  const loadFile = async (path) => {
    try {
      setStatus(`載入 ${path}`);
      const resp = await axios.get(`${BASE_URL}/sync/file`, { params: { path }, headers: { 'X-API-Key': API_KEY } });
      setContent(resp.data.content);
      setSelected(path);
      setStatus('完成');
    } catch (e) {
      setStatus('讀取失敗: ' + e.message);
    }
  };

  const setupWS = useCallback(() => {
    try {
      const wsUrl = BASE_URL.replace('http', 'ws') + '/ws/sync';
      const ws = new WebSocket(wsUrl);
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.type === 'update') loadManifest(true);
        } catch {}
      };
      ws.onclose = () => { setWsConnected(false); setTimeout(setupWS, 5000); };
      ws.onerror = () => { ws.close(); };
    } catch {}
  }, [loadManifest]);

  useEffect(() => { loadManifest(); setupWS(); }, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Modern Reader RN</Text>
      <Text style={styles.status}>{status} {wsConnected ? '🟢' : '🔴'}</Text>
      <FlatList
        data={files}
        keyExtractor={item => item.path}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item} onPress={() => loadFile(item.path)}>
            <Text style={styles.path}>{item.path}</Text>
            <Text style={styles.meta}>{item.sha256.slice(0,8)} | {item.category}</Text>
          </TouchableOpacity>
        )}
      />
      {selected && (
        <View style={styles.detailBox}>
          <Text style={styles.detailTitle}>{selected}</Text>
          <Text style={styles.detailContent}>{content}</Text>
          <TouchableOpacity onPress={() => setSelected(null)} style={styles.closeBtn}><Text style={styles.closeTxt}>關閉</Text></TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#111', padding: 16 },
  title: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 4 },
  status: { color: '#ccc', marginBottom: 12 },
  item: { paddingVertical: 8, borderBottomColor: '#333', borderBottomWidth: 1 },
  path: { color: '#fff', fontSize: 14 },
  meta: { color: '#888', fontSize: 12 },
  detailBox: { position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: '#222', padding: 12, borderTopWidth: 1, borderTopColor: '#333', maxHeight: '45%' },
  detailTitle: { color: '#fff', fontSize: 16, fontWeight: 'bold', marginBottom: 8 },
  detailContent: { color: '#ddd', fontSize: 12 },
  closeBtn: { marginTop: 10, backgroundColor: '#444', padding: 8, alignItems: 'center', borderRadius: 6 },
  closeTxt: { color: '#fff' }
});
