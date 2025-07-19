import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CheckCircle, XCircle, Search, FileText, Loader2 } from 'lucide-react'
import './App.css'

interface DocumentInfo {
  id: string
  url: string
  accessible: boolean
  title?: string
  content_preview?: string
  error?: string
}

interface TestResult {
  base_id: string
  strategies: string[]
  total_tested: number
  successful_count: number
  failed_count: number
  success_rate: number
  successful_documents: DocumentInfo[]
  failed_documents: DocumentInfo[]
}

const API_BASE = 'http://localhost:8000'

function App() {
  const [baseDocId, setBaseDocId] = useState('11ql80LUVCpuk-tyW0oZ0Pf-v0NmEbXuC5115fSAX-io')
  const [testResults, setTestResults] = useState<TestResult | null>(null)
  const [knownDocs, setKnownDocs] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [selectedStrategies, setSelectedStrategies] = useState(['last_char', 'last_digit'])
  const [maxIncrements, setMaxIncrements] = useState(10)
  const [testDelay, setTestDelay] = useState(1.0)

  const strategies = [
    { id: 'last_char', label: 'Last Character', description: 'Increment the last character' },
    { id: 'last_digit', label: 'Last Digit', description: 'Increment the last digit found' },
    { id: 'last_letter', label: 'Last Letter', description: 'Increment the last letter found' },
    { id: 'all_positions', label: 'All Positions', description: 'Try incrementing each position' }
  ]

  useEffect(() => {
    loadKnownDocuments()
  }, [])

  const loadKnownDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/test-known-documents`, {
        method: 'POST'
      })
      const data = await response.json()
      setKnownDocs(data)
    } catch (error) {
      console.error('Failed to load known documents:', error)
    }
  }

  const testIncrements = async () => {
    if (!baseDocId.trim()) return

    setLoading(true)
    setProgress(0)
    setTestResults(null)

    try {
      const response = await fetch(`${API_BASE}/test-increments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          base_id: baseDocId.trim(),
          strategies: selectedStrategies,
          max_increments: maxIncrements,
          test_delay: testDelay
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setTestResults(data)
      setProgress(100)
    } catch (error) {
      console.error('Test failed:', error)
      alert(`Test failed: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const testSingleDocument = async (docId: string) => {
    try {
      const response = await fetch(`${API_BASE}/test-document/${encodeURIComponent(docId)}`, {
        method: 'POST'
      })
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Single document test failed:', error)
      return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Google Docs Harvester</h1>
          <p className="text-lg text-gray-600">
            Discover publicly accessible Google Docs through ID pattern analysis
          </p>
        </div>

        <Tabs defaultValue="test" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="test">Test Increments</TabsTrigger>
            <TabsTrigger value="known">Known Documents</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          <TabsContent value="test" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Document ID Testing
                </CardTitle>
                <CardDescription>
                  Enter a base Google Doc ID and test incremental variations to discover new documents
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Base Document ID</label>
                  <Input
                    value={baseDocId}
                    onChange={(e) => setBaseDocId(e.target.value)}
                    placeholder="Enter Google Doc ID..."
                    className="font-mono text-sm"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Max Increments</label>
                    <Input
                      type="number"
                      value={maxIncrements}
                      onChange={(e) => setMaxIncrements(parseInt(e.target.value) || 10)}
                      min="1"
                      max="100"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Test Delay (seconds)</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={testDelay}
                      onChange={(e) => setTestDelay(parseFloat(e.target.value) || 1.0)}
                      min="0.1"
                      max="10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Increment Strategies</label>
                  <div className="grid grid-cols-2 gap-2">
                    {strategies.map((strategy) => (
                      <div key={strategy.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={strategy.id}
                          checked={selectedStrategies.includes(strategy.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedStrategies([...selectedStrategies, strategy.id])
                            } else {
                              setSelectedStrategies(selectedStrategies.filter(s => s !== strategy.id))
                            }
                          }}
                          className="rounded"
                        />
                        <label htmlFor={strategy.id} className="text-sm">
                          <div className="font-medium">{strategy.label}</div>
                          <div className="text-gray-500 text-xs">{strategy.description}</div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <Button 
                  onClick={testIncrements} 
                  disabled={loading || !baseDocId.trim() || selectedStrategies.length === 0}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Testing Documents...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Test Incremental IDs
                    </>
                  )}
                </Button>

                {loading && (
                  <div className="space-y-2">
                    <Progress value={progress} className="w-full" />
                    <p className="text-sm text-gray-600 text-center">
                      Testing document variations...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="known" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Known Documents
                </CardTitle>
                <CardDescription>
                  Documents that are confirmed to be publicly accessible
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {knownDocs.map((doc, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            {doc.accessible ? (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-500" />
                            )}
                            <span className="font-medium text-sm">{doc.title || 'Untitled'}</span>
                          </div>
                          <div className="font-mono text-xs text-gray-600 break-all">
                            {doc.id}
                          </div>
                          {doc.content_preview && (
                            <div className="text-xs text-gray-500 line-clamp-2">
                              {doc.content_preview}
                            </div>
                          )}
                        </div>
                        <Badge variant={doc.accessible ? "default" : "destructive"}>
                          {doc.accessible ? "Accessible" : "Error"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-4">
            {testResults ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Test Results Summary</CardTitle>
                    <CardDescription>
                      Results from testing incremental variations of: {testResults.base_id}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold">{testResults.total_tested}</div>
                        <div className="text-sm text-gray-600">Total Tested</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">{testResults.successful_count}</div>
                        <div className="text-sm text-gray-600">Found</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-red-600">{testResults.failed_count}</div>
                        <div className="text-sm text-gray-600">Not Found</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{(testResults.success_rate * 100).toFixed(1)}%</div>
                        <div className="text-sm text-gray-600">Success Rate</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {testResults.successful_count > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-green-600">🎉 Discovered Documents</CardTitle>
                      <CardDescription>
                        New publicly accessible documents found through ID incrementation
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {testResults.successful_documents.map((doc, index) => (
                          <div key={index} className="border border-green-200 rounded-lg p-3 bg-green-50">
                            <div className="flex items-start justify-between">
                              <div className="flex-1 space-y-1">
                                <div className="flex items-center gap-2">
                                  <CheckCircle className="h-4 w-4 text-green-500" />
                                  <span className="font-medium">{doc.title || 'Untitled Document'}</span>
                                </div>
                                <div className="font-mono text-xs text-gray-600 break-all">
                                  {doc.id}
                                </div>
                                <a 
                                  href={doc.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-xs text-blue-600 hover:underline"
                                >
                                  Open Document →
                                </a>
                                {doc.content_preview && (
                                  <div className="text-xs text-gray-700 mt-2 p-2 bg-white rounded border">
                                    {doc.content_preview}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-gray-500">No test results yet. Run a test to see results here.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
